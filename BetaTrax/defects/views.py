from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, TemplateHTMLRenderer, JSONRenderer
from urllib.parse import quote_plus

from comments.models import Comment

from .models import DefectReport
from .serializers import DefectReportSerializer, DefectReportStatusSerializer, DefectEvaluationSerializer
from .product_owner_confirm_views import ProductOwnerConfirmViewsMixin
from .product_owner_retest_views import ProductOwnerRetestViewsMixin
from .developer_views import DeveloperViewsMixin
from .developer_metrics import build_metrics_response


class DefectReportViewSet(
    ProductOwnerConfirmViewsMixin,
    ProductOwnerRetestViewsMixin,
    DeveloperViewsMixin,
    viewsets.ModelViewSet
):
    queryset = DefectReport.objects.all()
    serializer_class =  DefectReportSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer]
    # renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    search_fields = ["ReportTitle", "TesterID"]

    def get_queryset(self):
        queryset = DefectReport.objects.all()
        TargetedStatus = self.request.query_params.get("Status")
        if TargetedStatus is not None:
            queryset = queryset.filter(Status = TargetedStatus)
        return queryset

    def list(self, request, *args, **kwargs):
        """Override list to render an HTML template when HTML is requested.

        - If the client accepts HTML, render 'defects/reports.html' with the defects queryset.
        - Otherwise, return the normal JSON serialized response.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # If the request will be rendered as HTML, return a rendered template
        if request.accepted_renderer.format == 'html':
            # Use Django's render to return a TemplateResponse
            return render(request, 'defects/reports.html', {'defects': queryset})

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Render an HTML detail page when HTML is requested, otherwise return JSON."""
        defect = self.get_object()
        if request.accepted_renderer.format == 'html':
            comments = Comment.objects.filter(defect=defect).order_by('-created_at')[:50]
            context = {
                'defect': defect,
                'comments': comments,
                'severity_choices': DefectReport.SeverityC,
                'priority_choices': DefectReport.PriorityC,
            }
            return render(request, 'defects/defect_detail.html', context)

        serializer = self.get_serializer(defect)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        
        data["Status"] = "New"
        serializers =  self.get_serializer(data = data)
        serializers.is_valid(raise_exception = True)
        self.perform_create(serializers)
        return Response(serializers.data, status = status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', 'post'], url_path='submit')
    def submit_defect(self, request):
        if request.method == 'POST':
            # if not request.user.groups.filter(name='BetaTester').exists():
            #     error_msg = "Only Testers can submit new defect reports."
            #     if request.accepted_renderer.format == 'json':
            #         return Response({"detail": error_msg}, status=status.HTTP_403_FORBIDDEN)
            #     messages.error(request, error_msg)
            #     return redirect('defectreport-list')

            data = request.data.copy()
            # Force status to New and prevent submitters from setting Severity/Priority
            data['Status'] = 'New'
            data.pop('Severity', None)
            data.pop('Priority', None)

            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                
                if request.accepted_renderer.format == 'json':
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                
                messages.success(request, "Defect report submitted successfully!")
                return redirect('defectreport-list')
            if request.accepted_renderer.format == 'json':
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return render(request, 'defects/submit_defect.html', {'errors': serializer.errors})
        return render(request, 'defects/submit_defect.html')

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
        permission_classes=[IsAuthenticated],
        renderer_classes=[JSONRenderer, BrowsableAPIRenderer],
    )
    def change_status(self, request, pk=None):
        defect = self.get_object()
        
        if "Status" not in request.data:
            return Response(
                {"Status": "This field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.data.get("Status") == defect.Status:
            return Response(
                {"Status": f"Defect is already '{defect.Status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = DefectReportStatusSerializer(
            defect,
            data=request.data,
            context={"request": request},
            partial=False,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": f"Defect status updated to {defect.Status}.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        user = request.user
        links = []
        role = "Anonymous"
        if user.is_authenticated:
            if user.groups.filter(name='ProductOwner').exists():
                role = "Product Owner"
                links = [
                    {'name': 'New Reports (Pending Evaluation)', 'url': '/defects/reports/new', 'method': 'GET'},
                    {'name': 'Open Defects (Ready to Assign)', 'url': '/defects/reports/open', 'method': 'GET'},
                    {'name': 'Developer Ratings', 'url': '/defects/reports/developers/', 'method': 'GET'},
                    {'name': 'All Reports', 'url': '/defects/reports/', 'method': 'GET'},
                    {'name': 'Open Fixed Defects', 'url': '/resolved/', 'method': 'GET'},
                    {'name': 'Add New Product', 'url': '/product_reg/dashboard/', 'method': 'GET'}
                ]
            elif user.groups.filter(name='Developer').exists():
                role = 'Developer'
                links = [{"name": "My Assigned Tasks", "url": "/defects/reports/?Status=Assigned", "method": "GET"},
                         {"name": "Open Defects (Available)", 'url': '/defects/reports/open', "method": 'GET'},]
            else:
                role = 'Authenticated User (No Role)'
                links = [{"name": "View All Reports", 'url': '/defects/reports/', 'method': 'GET'},]
        else:
            links = [{"name": "Login", "url": "/admin/login/", "method": "GET"},
                {"name": "View All Reports (Read Only)", "url": "/defects/reports/", "method": "GET"},]
      
        # If the client accepts HTML, render a simple dashboard page.
        if request.accepted_renderer.format == 'html':
            context = {
                'username': user.username if user.is_authenticated else 'Not logged in',
                'role': role,
                'links': links,
            }
            return render(request, 'defects/dashboard.html', context)

        return Response({'username': user.username if user.is_authenticated else 'Not logged in','role': role,'links': links,})
  
    @action(detail=True, methods=['patch'], url_path='accept', permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        defect = self.get_object()
        
        if not request.user.groups.filter(name='ProductOwner').exists():
            return Response(
                {"detail": "Only Product Owners can accept reports."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if defect.Status != 'New':
            return Response(
                {"error": 'Only New reports can be accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        severity = request.data.get("Severity")
        priority = request.data.get("Priority")
        if not severity or not priority:
            return Response(
                {'error': 'Severity and Priority are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        defect.Status = "Open"
        defect.Severity = severity
        defect.Priority = priority
        defect.save()
        
        return Response(
            {
                "status": 'accepted',
                "id": defect.id,
                "Severity": defect.Severity,
                "Priority": defect.Priority,
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get", "post"], url_path="evaluate", permission_classes=[IsAuthenticatedOrReadOnly])
    def evaluate(self, request, pk=None):
        defect = self.get_object()
        serializer = None

        if request.method == 'POST':
            if not request.user.groups.filter(name='ProductOwner').exists():
                error_msg = "Only Product Owners can evaluate reports."
                if request.accepted_renderer.format == 'json':
                    return Response({"detail": error_msg}, status=status.HTTP_403_FORBIDDEN)
                messages.error(request, error_msg)
                return redirect('defectreport-detail', pk=defect.pk)
            mutable_data = request.data.copy()
            if 'accept' in request.data: mutable_data['action'] = 'accept'
            elif 'reject' in request.data: mutable_data['action'] = 'reject'
            elif 'duplicate' in request.data: mutable_data['action'] = 'duplicate'
            
            serializer = DefectEvaluationSerializer(defect, data=mutable_data, context={'request': request})
            
            if serializer.is_valid():
                serializer.save()
                
                if request.accepted_renderer.format == 'json':
                    return Response({
                        "message": f"Report #{defect.id} successfully updated.",
                        "status": defect.Status
                    }, status=status.HTTP_200_OK)

                messages.success(request, f"Report #{defect.id} updated.")
                return redirect('defectreport-evaluate-success', pk=defect.pk)

            if request.accepted_renderer.format == 'json':
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            messages.error(request, "Please fix the errors below.")

    
        comments = Comment.objects.filter(defect=defect).order_by('-created_at')[:50]
        
        context = {
            'defect': defect, 
            'comments': comments, 
            'severity_choices': DefectReport.SeverityC, 
            'priority_choices': DefectReport.PriorityC,
            'errors': serializer.errors if serializer else None  # Pass errors to the UI
        }
        return render(request, 'defects/defect_evaluation.html', context)
    
    @action(detail=True, methods=["get"], url_path="evaluate-success", renderer_classes=[TemplateHTMLRenderer])
    def evaluate_success(self, request, pk=None):
        defect = self.get_object()
        context = {'defect': defect}
        return render(request, 'defects/evaluation_success.html', context)

    @action(detail=False, methods=['get'], url_path='open', renderer_classes=[TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer])
    def open_defects(self, request):
        # Show both Open and Reopened defects
        defects = DefectReport.objects.filter(Q(Status='Open') | Q(Status='Reopened')).order_by('CreatedTime')
        if request.accepted_renderer.format == 'json':
            serializer = self.get_serializer(defects, many=True)
            return Response(serializer.data) # Returns clean JSON
        return render(request, 'defects/open_defects.html', {'defects': defects})

    @action(detail=True, methods=['post'], url_path='take', permission_classes=[IsAuthenticated], renderer_classes=[TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer])
    def take(self, request, pk=None):
        defect = self.get_object()
        is_not_open = defect.Status not in ['Open', 'Reopened']
        is_not_developer = not request.user.groups.filter(name='Developer').exists()

        if is_not_open or is_not_developer:
            error_msg = 'Cannot take this defect.'
            if is_not_open: error_msg += " Status is not Open or Reopened."
            if is_not_developer: error_msg += " You are not in the Developer group."
            if request.accepted_renderer.format == 'json':
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            

            messages.error(request, error_msg)
            return redirect('defectreport-open-defects')

        defect.assigned_to = request.user
        defect.Status = 'Assigned'
        defect.save()
        
        if request.accepted_renderer.format == 'json':
            serializer = self.get_serializer(defect)
            return Response(serializer.data)
        
        Comment.objects.create(author=request.user, text=f"System: Defect #{defect.id} assigned to {request.user.username}.")
        messages.success(request, "Success! Defect assigned.")
        return render(request, 'defects/take_success.html', {'defect': defect})
    
    @action(detail=False, methods=['get'], url_path='new', permission_classes=[IsAuthenticated])
    def new_defects(self, request):
        """API endpoint for Product Owner: list all defects with Status='New'."""
        defects = self.get_queryset().filter(Status='New')
        # If HTML is requested, render a template for browser clients.
        if request.accepted_renderer.format == 'html':
            return render(request, 'defects/new_defects.html', {'defects': defects})
        serializer = self.get_serializer(defects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my-assigned', permission_classes=[IsAuthenticated])
    def my_assigned_defects(self, request):
        """API endpoint for Developer: list defects assigned to current user with Status='Assigned'."""
        defects = self.get_queryset().filter(assigned_to=request.user, Status='Assigned')
        serializer = self.get_serializer(defects, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='my-tasks', permission_classes=[IsAuthenticated])
    def my_tasks(self, request):
        if not request.user.groups.filter(name='Developer').exists():
            return Response(
                {'error': 'Only developers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tasks = DefectReport.objects.filter(assigned_to=request.user, Status='Assigned')
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["get", "post"], url_path='mark_fixed', permission_classes=[IsAuthenticated])
    def mark_fixed(self, request, pk=None):
        defect = self.get_object()
        
        if defect.Status != "Assigned" or defect.assigned_to != request.user:
            return Response(
                {'error': 'Only assigned developer can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == "POST":
            serializer = DefectReportStatusSerializer(
                defect,
                data={
                    "Status": "Fixed"
                },
                context={"request": request},
                partial=False,
            )
            if not serializer.is_valid():
                messages.error(request, "Unable to mark this defect as Fixed.")
                return render(
                    request,
                    'defects/mark_fixed.html',
                    context={"defect": defect, "errors": serializer.errors},
                    status=400,
                )
            serializer.save()
            return redirect("assigned_defects")
        return render(request, 'defects/mark_fixed.html', context={"defect": defect})
    @action(detail=False, methods=['get'], url_path='developer-metrics/(?P<user_id>[0-9]+)', permission_classes=[IsAuthenticated])
    def developer_metrics(self, request, user_id=None):
        """Return effectiveness rating for a developer."""
        from .models import DeveloperMetrics

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        metrics, _ = DeveloperMetrics.objects.get_or_create(user=user)
        fixed = metrics.defects_fixed
        reopened = metrics.defects_reopened
        return Response(build_metrics_response(user, fixed, reopened))

    @action(detail=False, methods=['get'], url_path='developers', permission_classes=[IsAuthenticated])
    def developers(self, request):
        """List developer ratings with links to individual profiles (Product Owner only)."""
        if not request.user.groups.filter(name='ProductOwner').exists():
            return Response(
                {"detail": "Only Product Owners can view developer ratings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        developers = User.objects.filter(groups__name='Developer').distinct().order_by('username')
        rows = []
        for developer in developers:
            payload = build_metrics_response(
                user=developer,
                defects_fixed=getattr(developer, 'developer_metrics', None).defects_fixed if hasattr(developer, 'developer_metrics') else 0,
                defects_reopened=getattr(developer, 'developer_metrics', None).defects_reopened if hasattr(developer, 'developer_metrics') else 0,
            )
            payload['profile_url'] = f"/defects/reports/developer-profile/{developer.id}/"
            rows.append(payload)

        if request.accepted_renderer.format == 'html':
            return render(request, 'defects/developer_metrics_list.html', {'developers': rows})

        return Response(rows)

    @action(detail=False, methods=['get'], url_path='developer-profile/(?P<user_id>[0-9]+)', permission_classes=[IsAuthenticated])
    def developer_profile(self, request, user_id=None):
        """Show a developer profile with rating details (Product Owner only)."""
        if not request.user.groups.filter(name='ProductOwner').exists():
            return Response(
                {"detail": "Only Product Owners can view developer profiles."},
                status=status.HTTP_403_FORBIDDEN,
            )

        developer = get_object_or_404(User, pk=user_id)
        if not developer.groups.filter(name='Developer').exists():
            return Response(
                {"detail": "Requested user is not a developer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        metrics = getattr(developer, 'developer_metrics', None)
        defects_fixed = metrics.defects_fixed if metrics else 0
        defects_reopened = metrics.defects_reopened if metrics else 0
        payload = build_metrics_response(developer, defects_fixed, defects_reopened)
        payload['account_created_at'] = developer.date_joined
        payload['profile_picture_url'] = (
            f"https://ui-avatars.com/api/?name={quote_plus(developer.username)}&background=0B7285&color=FFFFFF&size=256"
        )

        if request.accepted_renderer.format == 'html':
            return render(request, 'defects/developer_profile.html', {'developer': payload})

        return Response(payload)