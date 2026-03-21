# BetaTraxService: Software as a Service (SaaS) for Beta Testing

**COMP3297 Software Engineering - Group Project (Summer 2026)**
The University of Hong Kong

This repository contains the code and resources for our group project focused on BetaTrax, a service that supports beta 
testing programmes by managing the beta defect resolution workflow and tracking reported defects through their lifecycles. 
The service will be used by the Product Owner, Developers and Beta Testers.

## Project Overview

Beta Testing Workflow:

Beta Tester submits defect report --> Product Owner accepts report --> Developer assigns defect to oneself --> 
Develop fixes defect --> Beta Tester retests defect --> Product Owner marks defect as solved 

As the number of beta testers has grown, the manual handling of defect reports is becoming infeasible. In addition, it is 
no longer possible to keep an adequate history of defect resolution and decisions made during that process. The  BetaTrax 
service has thus been developed to solve these problems.  It will be used for all the company’s products and, in the 
future, may be rolled out as a product itself, for adoption by other software development companies. 

Service Structure:

1. **Dashboard:** Top navigation bar with role‑based links.
2. **Tester Submission View:** Area to allow Tester to submit defect report and optional email.
3. **Defect List(Evaluation)** List that allows Product Owners to check on submitted defect reports. Product Owners can click on a report to accept or reject it.
4. **Product Owner Evaluation View:** Area to allow Product Owners to accepet or reject report.
5. **Defect List(Assignment):** List that allows Developers to check on all accepted defect reports. Developers can click on chosen reports to assign themselves to the corresponding defect.
6. **Defect List(Assigned):** List that allows Developers to check on all defect reports they have been assigned to.
7. **Tester Retest View:** Area to allow Tester to comment on defect after a Developer modified the code.
8. **Product Owner Confirm View:** Area to allow Product Owner to marks defect as solved or reopen if failed.
9. **Comment Section:** Section that display progress on all defects. Product Owners and Developer can click on individual comments to enact Evaluation/Assignment/Vertification.

