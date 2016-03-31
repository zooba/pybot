'''Deployment script for DoIStillHaveAJob

This script will deploy the DoIStillHaveAJob web site in a new resource group.
After deployment, the script will offer to open the site, and then delete all
resources associated with it.

Before running this script, see the section and link below on providing
credentials to your Azure account.
'''

__author__ = "Steve Dower <steve.dower@microsoft.com>"
__version__ = "1.0.0"

import sys
import uuid

#################################################
#region Credential Boilerplate

# See http://azure-sdk-for-python.readthedocs.org/en/latest/resourcemanagementauthentication.html
# for info about setting CREDENTIALS

from azure.common.credentials import UserPassCredentials
try:
    CREDENTIALS = UserPassCredentials(
        '<Azure Active Directory username>',
        '<password>',
    )
except:
    CREDENTIALS = None

# SUBSCRIPTION_ID should be a subscription that can be accessed with the
# above credentials. If not provided, a list of available subscriptions will
# be displayed and the script will exit.
SUBSCRIPTION_ID = ''

try:
    # Credentials may be kept in a separate file outside of source control.
    from deploy_credentials import CREDENTIALS, SUBSCRIPTION_ID
except ImportError:
    pass

if not CREDENTIALS:
    print("The provided credentials were invalid.", file=sys.stderr)
    print("Review deploy.py and update deployment settings as necessary.", file=sys.stderr)
    sys.exit(1)

if not SUBSCRIPTION_ID:
    # Display a list of available subscriptions if SUBSCRIPTION_ID was not given

    from azure.mgmt.resource.subscriptions import SubscriptionClient, SubscriptionClientConfiguration
    sc = SubscriptionClient(SubscriptionClientConfiguration(CREDENTIALS))
    print('SUBSCRIPTION_ID was not provided. Select an id from the following list.')
    for sub in sc.subscriptions.list():
        print('    {}: {}'.format(sub.subscription_id, sub.display_name))
    sys.exit(1)

#endregion
#################################################

from azure.mgmt.resource.resources import ResourceManagementClientConfiguration, ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClientConfiguration, WebSiteManagementClient

from azure.mgmt.resource.resources.models import ResourceGroup, DeploymentProperties, DeploymentMode


#################################################
# Constants for this deployment.
#
# Some names include random UUIDs to avoid collisions.
# These are not necessary in controlled environments.

RESOURCE_GROUP = "pybot" + uuid.uuid4().hex
LOCATION = "West US"

COMPANY_NAME = "Contoso"
DEPLOYMENT = "ContosoBots"
WEBSITE = "pybot" + uuid.uuid4().hex[:8].lower()
STORAGE = 's' + uuid.uuid4().hex[:23].lower()

WEBSITE_SOURCE = "https://github.com/zooba/pybot.git"


#################################################
# Create management clients

rc = ResourceManagementClient(ResourceManagementClientConfiguration(
    credentials=CREDENTIALS,
    subscription_id=SUBSCRIPTION_ID,
))
ws = WebSiteManagementClient(WebSiteManagementClientConfiguration(
    credentials=CREDENTIALS,
    subscription_id=SUBSCRIPTION_ID,
))


#################################################
# Create a resource group
#
# A resource group contains our entire deployment
# and makes it easy to manage related services.

print("Creating resource group:", RESOURCE_GROUP)

rc.resource_groups.create_or_update(RESOURCE_GROUP, ResourceGroup(location=LOCATION))

#################################################
# Deploy a resource manager template
#
# This template defines our entire service, including
# the storage account and website. After deployment
# is complete, our site is ready to use.
#
# Available arguments for templates can be found
# at http://aka.ms/arm-template and http://resources.azure.com

print("Deploying:", DEPLOYMENT)

TEMPLATE = {
  "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  # These parameters may be referred to throughout the template.
  # They will be filled in below from PARAMETERS
  "parameters": {
    "siteName": { "type": "string" },
    "hostingPlanName": { "type": "string", "defaultValue": "InternalApps" },
    "storageName": { "type": "string" },
    "siteLocation": { "type": "string" },
    "repoUrl": { "type": "string" },
    "companyName": { "type": "string", "defaultValue": COMPANY_NAME },
  },
  "resources": [
    # Create a server farm for us to run our web site in
    {
      "apiVersion": "2015-08-01",
      "name": "[parameters('hostingPlanName')]",
      "type": "Microsoft.Web/serverfarms",
      "location": "[parameters('siteLocation')]",
      "sku": { "name": "F1" },
    },
    ## Create a storage account for our table
    #{
    #  "apiVersion": "2015-05-01-preview",
    #  "name": "[parameters('storageName')]",
    #  "type": "Microsoft.Storage/storageAccounts",
    #  "location": "[parameters('siteLocation')]",
    #  "properties": {
    #    "accountType": "Standard_LRS"
    #  }
    #},
    # Create and configure our web site
    {
      "apiVersion": "2015-08-01",
      "name": "[parameters('siteName')]",
      "type": "Microsoft.Web/sites",
      "location": "[parameters('siteLocation')]",
      "dependsOn": [ "[resourceId('Microsoft.Web/serverfarms', parameters('hostingPlanName'))]" ],
      "properties": {
        "serverFarmId": "[parameters('hostingPlanName')]",
      },
      "resources": [
        # Configure appsettings for the website. These will be
        # available within our handler as environment variables.
        {
          "apiVersion": "2015-08-01",
          "name": "appsettings",
          "type": "config",
          "dependsOn": [
            "[resourceId('Microsoft.Web/Sites', parameters('siteName'))]",
            #"[resourceId('Microsoft.Storage/storageAccounts', parameters('storageName'))]",
          ],
          "properties": {
            "COMPANY_NAME": "[parameters('companyName')]",

            ## Calculate the name and key from the storage account we
            ## just created.
            #"STORAGE_ACCOUNT_NAME": "[parameters('storageName')]",
            #"STORAGE_ACCOUNT_KEY": "[listkeys(" +
            #"resourceId('Microsoft.Storage/storageAccounts', parameters('storageName')), " +
            #  "'2015-05-01-preview'" +
            #").key1]",
            
            # Not very secret, but this is just for fun
            "APP_ID": "mybotapp",
            "APP_SECRET": "3c8a5686b1b14135b9112620603c5575",
          }
        },

        # Configure deployment from source control
        {
          "apiVersion": "2015-08-01",
          "name": "web",
          "type": "sourcecontrols",
          "dependsOn": [ 
            "[resourceId('Microsoft.Web/Sites', parameters('siteName'))]",
            "[resourceId('Microsoft.Web/Sites/config', parameters('siteName'), 'appSettings')]",
          ],
          "properties": {
            "repoUrl": "[parameters('repoUrl')]",
            "branch": "master",
            "isManualIntegration": True,
          }
        },
      ]
    },
  ]
}

# PARAMETERS will be merged with TEMPLATE on the server to produce
# our specific deployment. This allows templates to be reused without
# modification.
PARAMETERS = {
    "siteLocation": { "value": LOCATION },
    "siteName": { "value": WEBSITE },
    "storageName": { "value": STORAGE },
    "repoUrl": { "value": WEBSITE_SOURCE },
}

rc.deployments.create_or_update(
    RESOURCE_GROUP,
    DEPLOYMENT,
    properties=DeploymentProperties(
        mode=DeploymentMode.incremental,
        template=TEMPLATE,
        parameters=PARAMETERS,
    )
).result()

#################################################
# Get our website's URL
#
# The URL is generally predictable, but may be
# affected by configuration in the template.

conf = ws.sites.get_site(RESOURCE_GROUP, WEBSITE)
print()
print('Bot is available at:')
for name in conf.host_names:
    print('   ', name)
print()

#################################################
# Delete the resource group
#
# This quickly cleans up all of our resources.

print()
if input("Delete resource group? [y/N] "):
    rc.resource_groups.delete(RESOURCE_GROUP).result()
