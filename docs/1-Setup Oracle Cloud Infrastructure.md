# Setup Oracle Cloud Infrastructure

> **Note:** These steps are mandatory only if you plan to use OCI metrics data to monitor **MySQL HeatWave** instances. If not, you may skip this section entirely.

### Setup Identity Domain and Dynamic Group

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









