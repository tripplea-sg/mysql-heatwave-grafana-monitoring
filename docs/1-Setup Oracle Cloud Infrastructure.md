# Setup Oracle Cloud Infrastructure
This steps are mandatory only if you're planning to use OCI metrics data to monitor MySQL HeatWave instances, otherwise you may skip this steps entirely.

### Setup Domain and Dynamic-group
To setup IAM policy, ensure your tenancy has an `Identity Domain`. If doesn't have, then create a new identity domain: <br>
Go to `Identity & Security`, then `Domains`. Click `Create Domain`. Refer to the following OCI documentation on creating new identity domains: 
https://docs.oracle.com/en-us/iaas/Content/Identity/domains/to-create-new-identity-domain.htm <br>

Then, create a `Dynamic-group`. Go to tab `Dynamic-Group` and create new under your identity domain. Add the following matching rule:
```
ALL{instance.compartment.id = 'compartment OCID'}
```
Change the `compartment OCID` with your `compartment OCID`. Refer to the following online documentation on how to get your `compartment OCID`: https://docs.oracle.com/en-us/iaas/Content/GSG/Tasks/contactingsupport_topic-Locating_Oracle_Cloud_Infrastructure_IDs.htm <br>
<br>
If you are the tenancy owner, then you may use your `tenancy OCID` as `compartment OCID`. <br><br>
Refer to the following online documentation on how to create a `Dynamic-group`: https://docs.oracle.com/en-us/iaas/Content/Identity/dynamicgroups/To_create_a_dynamic_group.htm
<br><br>
And refer to the following online documentation on how to write a matching rule to define `dynamic-group`: https://docs.oracle.com/en-us/iaas/Content/Identity/dynamicgroups/Writing_Matching_Rules_to_Define_Dynamic_Groups.htm

### Setup Policies








