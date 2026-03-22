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
5. **Product Owner View:** List that allow Product Owners to keep track of reports that can be assigned.
6. **Defect List(Assignment):** List that allows Developers to check on all accepted defect reports. Developers can click on chosen reports to assign themselves to the corresponding defect.
7. **Defect List(Assigned):** List that allows Developers to check on all defect reports they have been assigned to.
8. **Tester Retest View:** Area to allow Tester to comment on defect after a Developer modified the code.
9. **Product Owner Confirm View:** Area to allow Product Owner to marks defect as solved or reopen if failed.
10. **Comment Section:** Section that display progress on all defects. Product Owners and Developer can click on individual comments to enact Evaluation/Assignment/Vertification.

## Team Members

<!-- markdownlint-disable MD033 -->

<table>
    <tbody>
        <tr>
            <th>Name</th>
            <th>UID</th>
            <th>Profile</th>
        </tr>
        <tr>
            <td>Tam Ho Chun</td>
            <td>3036218342</td>
            <td><a href="https://github.com/mct61674"><img src="https://avatars.githubusercontent.com/u/185241369?v=4" alt="Tam Ho Chun" width=50></a></td>
        </tr>
        <tr>
            <td>Lam Cheung Lam Nicholas</td>
            <td>3036220498</td>
            <td><a href="https://github.com/SuperNicky12"><img src="https://avatars.githubusercontent.com/u/182529378?v=4" alt="Lam Cheung Lam Nicholas" width=50></a></td>
        </tr>
        <tr>
            <td>Chan Hin Chun Jensen</td>
            <td>3036218017</td>
            <td><a href="https://github.com/JChan-cs"><img src="https://avatars.githubusercontent.com/u/158464686" alt="Chan Hin Chun Jensen" width=50></a></td>
        </tr>
        <tr>
            <td>Wong King Wang</td>
            <td>3036221040</td>
            <td><a href="https://github.com/KWHK0626"><img src="https://avatars.githubusercontent.com/u/186687273?v=4" alt="Wong King Wang" width=50></a></td>
        </tr>
        <tr>
            <td>Ho Kin Sang</td>
            <td>3036080002</td>
            <td><a href="https://github.com/Sangho12"><img src="https://avatars.githubusercontent.com/u/159551341?v=4" alt="Ho Kin Sang" width=50></a></td>
        </tr>
    </tbody>
</table>

<!-- markdownlint-enable MD033-->

# Repository structure

# References

[Back to top](#️-BetaTraxService:-Software-as-a-Service-(SaaS)-for-Beta-Testing)
