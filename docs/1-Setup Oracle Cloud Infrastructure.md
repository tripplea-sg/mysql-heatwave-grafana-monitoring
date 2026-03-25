# Setup Oracle Cloud Infrastructure

> **Note:** These steps are mandatory only if you plan to use OCI metrics data to monitor **MySQL HeatWave** instances. If not, you may skip this section entirely.

### A. Setup Identity Domain and Dynamic Group

**1. Verify or Create an Identity Domain**
If you need to create a new **Identity Domain**, navigate to **Identity & Security** > **Domains** and click **Create Domain**.
*   **Reference:** [Creating an Identity Domain](https://docs.oracle.com/en-us/iaas/Content/Identity/domains/to-create-new-identity-domain.htm)

**2. Configure a Dynamic Group**
Ensure you have a **Dynamic Group** defined within your Identity Domain. To create one, navigate to the **Dynamic Groups** tab and click **Create Dynamic Group**.
*   **Reference:** [Managing Dynamic Groups](https://docs.oracle.com/en-us/iaas/Content/Identity/dynamicgroups/To_create_a_dynamic_group.htm)

**3. Define a Matching Rule**
Your Dynamic Group requires a matching rule to identify your monitoring instances. Use the following syntax:

```
ALL {instance.compartment.id = 'ocid1.compartment.oc1..example_ID'}
```
You may change compartment OCID with tenancy OCID if you are the tenancy owner or super-user.

---
### B. Setup IAM Policies

Navigate to **Identity & Security** > **Policies** and click **Create Policy**. Using the **Policy Builder** (Manual Editor), copy and paste the following statements:
```
Allow dynamic-group '<Domain_Name>'/'<Dynamic_Group_Name>' to read metrics in compartment <Compartment_Name>
Allow dynamic-group '<Domain_Name>'/'<Dynamic_Group_Name>' to read compartments in compartment <Compartment_Name>
Allow dynamic-group '<Domain_Name>'/'<Dynamic_Group_Name>' to read log-groups in compartment <Compartment_Name>
Allow dynamic-group '<Domain_Name>'/'<Dynamic_Group_Name>' to read log-content in compartment <Compartment_Name>
Allow dynamic-group '<Domain_Name>'/'<Dynamic_Group_Name>' to read all-resources in compartment <Compartment_Name>
```
#### Configuration Details

To finalize the policy, replace the placeholders in the snippet above with your specific environment details:

*   **`<Domain_Name>`/`<Dynamic_Group_Name>`**: Your Identity Domain and Dynamic Group names.
*   **`<Compartment_Name>`**: The specific compartment where your resources are located.

> **Note for Administrators:** If you are the **Tenancy Owner** or **Super-user**, you can replace `compartment <Compartment_Name>` with `tenancy` to apply the policy globally.

---
**Reference:** [Official OCI Documentation: Creating IAM Policies](https://docs.oracle.com/en/cloud/paas/integration-cloud/oracle-integration-oci/creating-iam-policy.html)

### C. Install OCI Data Source
Login to Grafana once it’s up as admin using password you just set. <br><br> Go to `connections`, then `data sources`. You will see `MySQL-Perf-Archive` already set for connection to repo DB. 
<br><br> Now we need to install oci-metric-datasource. Click `+ Add new data source` and search for `Oracle`  and select `Oracle Cloud Infrastructure Metrics`.









