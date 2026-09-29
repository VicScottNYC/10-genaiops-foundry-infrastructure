# Architecture — GenAIOps Microsoft Foundry Infrastructure

## 1. Purpose

This document describes the infrastructure architecture used to provision a Microsoft Foundry environment through Azure Developer CLI (`azd`) and modular Bicep Infrastructure as Code.

The architecture provides a reusable foundation for generative AI and agent workloads while separating environment-specific configuration from infrastructure implementation.

The validated deployment includes:

- Azure Resource Group
- Microsoft Foundry AI account
- Microsoft Foundry project
- `gpt-5-mini` model deployment
- Foundry capability host for hosted agents
- Log Analytics workspace
- Application Insights
- Azure Container Registry
- Application Insights project connection
- Azure Container Registry project connection

Additional Bicep modules provide conditional support for Storage, Azure AI Search, Bing Grounding, and Bing Custom Grounding.

Those optional modules are part of the infrastructure architecture but were not required for the validated base deployment.

---

## 2. Provisioning Architecture

The deployment begins from Azure Developer CLI:

```text
Developer
   |
   | azd up
   v
Azure Developer CLI
   |
   v
azure.yaml
   |
   v
infra/main.bicep
   |
   +--> Resource Group
   |
   +--> infra/core/ai/ai-project.bicep
             |
             +--> Foundry AI Account
             |
             +--> Foundry Project
             |
             +--> Model Deployment
             |
             +--> Managed Identities
             |
             +--> Azure RBAC
             |
             +--> Hosted-Agent Capability Host
             |
             +--> Monitoring
             |
             +--> Project Connections
             |
             +--> Conditional Dependent Resources
```

`azure.yaml` defines Bicep as the infrastructure provider and points Azure Developer CLI to:

```text
./infra
```

The root Bicep deployment then orchestrates the lower-level modules.

---

## 3. Infrastructure Layers

The architecture can be viewed as five layers:

```text
┌─────────────────────────────────────────────┐
│ Layer 1 — Deployment Orchestration          │
│ Azure Developer CLI                         │
│ azure.yaml                                  │
└──────────────────────┬──────────────────────┘
                       |
                       v
┌─────────────────────────────────────────────┐
│ Layer 2 — Subscription / Resource Group     │
│ infra/main.bicep                            │
└──────────────────────┬──────────────────────┘
                       |
                       v
┌─────────────────────────────────────────────┐
│ Layer 3 — Microsoft Foundry                 │
│ AI Account                                  │
│ Foundry Project                             │
│ Model Deployment                            │
│ Capability Host                             │
└──────────────────────┬──────────────────────┘
                       |
                       v
┌─────────────────────────────────────────────┐
│ Layer 4 — Platform Services                 │
│ Application Insights                        │
│ Log Analytics                               │
│ Azure Container Registry                    │
└──────────────────────┬──────────────────────┘
                       |
                       v
┌─────────────────────────────────────────────┐
│ Layer 5 — Optional Dependencies             │
│ Storage                                     │
│ Azure AI Search                             │
│ Bing Grounding                              │
│ Bing Custom Grounding                       │
└─────────────────────────────────────────────┘
```

This layered structure keeps the root deployment relatively small while delegating individual platform responsibilities to reusable modules.

---

## 4. Root Deployment

The root template is:

```text
infra/main.bicep
```

Its deployment scope is:

```bicep
targetScope = 'subscription'
```

This allows the template to create or target the resource group before deploying resource-group-scoped infrastructure.

The resource group follows the default naming convention:

```text
rg-${environmentName}
```

The root template then invokes:

```text
infra/core/ai/ai-project.bicep
```

at resource-group scope.

---

## 5. Foundry AI Account

The AI project module provisions a Cognitive Services account with:

```text
Kind: AIServices
SKU: S0
Identity: SystemAssigned
```

Important account settings include:

```text
allowProjectManagement = true
disableLocalAuth       = true
publicNetworkAccess    = Enabled
```

The system-assigned managed identity provides an Azure identity for the AI account.

Disabling local authentication reduces reliance on account-key authentication and supports an identity/RBAC-oriented access model.

The current template enables public network access. Private networking is not implemented by this project.

---

## 6. Foundry Project

The Foundry project is provisioned as:

```text
Microsoft.CognitiveServices/accounts/projects
```

and exists beneath the Foundry AI account:

```text
Foundry AI Account
        |
        v
Foundry Project
```

The project also receives:

```text
SystemAssigned Managed Identity
```

This provides the project with its own Azure identity for resource-access scenarios.

---

## 7. Model Deployment

Model deployments are defined declaratively.

The root infrastructure configuration includes:

```text
gpt-5-mini
```

using:

```text
Format: OpenAI
SKU: GlobalStandard
Capacity: 10
```

The AI project module creates deployments using:

```text
Microsoft.CognitiveServices/accounts/deployments
```

Conceptually:

```text
Deployment Configuration
        |
        v
deployments[]
        |
        v
Bicep Iteration
        |
        v
Foundry AI Account
        |
        v
gpt-5-mini
```

The implementation specifies:

```bicep
@batchSize(1)
```

which causes model deployments to be processed one at a time.

This can help avoid deployment conflicts when multiple model deployments are configured.

---

## 8. Hosted-Agent Capability

Hosted-agent support is controlled by:

```text
enableHostedAgents
```

When enabled, the template provisions:

```text
Microsoft.CognitiveServices/accounts/capabilityHosts
```

with:

```text
Name: agents
Capability Host Kind: Agents
```

The capability host configuration enables the public hosting environment.

The relationship is:

```text
Foundry AI Account
        |
        v
Capability Host
        |
        v
agents
```

The capability host establishes infrastructure support for hosted-agent deployment.

---

## 9. Observability Architecture

Monitoring is controlled by:

```text
enableMonitoring
```

which defaults to:

```text
true
```

When monitoring is enabled, the architecture provisions:

```text
Log Analytics Workspace
          |
          v
Application Insights
          |
          v
Foundry Project Connection
```

### Log Analytics

The Log Analytics module creates the workspace used by Application Insights.

### Application Insights

Application Insights is configured with the Log Analytics workspace ID.

### Foundry Connection

The Foundry project receives an Application Insights connection:

```text
appi-connection
```

This provides the infrastructure foundation required for later monitoring and tracing capabilities.

The existence of the observability infrastructure does not by itself imply that every application or agent telemetry scenario has been implemented.

---

## 10. Azure Container Registry

Azure Container Registry is represented by:

```text
infra/core/host/acr.bicep
```

The root infrastructure ensures that when hosted agents are enabled and no registry dependency is already supplied, a registry dependency is added.

Conceptually:

```text
enableHostedAgents
        |
        v
Check Registry Dependency
        |
        +-- Registry already configured --> use configuration
        |
        +-- Registry absent -------------> add registry dependency
                                                |
                                                v
                                      Azure Container Registry
                                                |
                                                v
                                      Foundry Project Connection
```

The validated deployment successfully created Azure Container Registry and its Foundry project connection.

---

## 11. Conditional Dependency Architecture

The project uses conditional Bicep modules to avoid provisioning every possible supporting service in every environment.

The supported dependent-resource types are:

```text
storage
registry
azure_ai_search
bing_grounding
bing_custom_grounding
```

The AI project module determines whether each dependency is present and conditionally invokes the corresponding module.

This pattern allows one infrastructure architecture to support multiple Foundry workload configurations.

---

## 12. Optional Storage

Storage is represented by:

```text
infra/core/storage/storage.bicep
```

It is deployed only when:

```text
resource == storage
```

exists in the dependent-resource configuration.

The module receives:

- Azure location
- Resource tags
- Resource name
- Connection name
- Principal ID
- Principal type
- AI Services account name
- Foundry project name

The module can therefore provision storage and associate it with the Foundry environment.

Storage was not required for the validated base deployment.

---

## 13. Optional Azure AI Search

Azure AI Search is represented by:

```text
infra/core/search/azure_ai_search.bicep
```

It is deployed only when:

```text
resource == azure_ai_search
```

is configured.

If Storage is also configured, the AI Search module can receive the resulting storage-account resource ID.

The architecture defines the knowledge container name as:

```text
knowledge
```

This creates an extensible infrastructure path for knowledge-grounded AI solutions.

Azure AI Search was not required for the validated base deployment.

---

## 14. Optional Grounding Infrastructure

Two grounding modules are represented:

```text
infra/core/search/bing_grounding.bicep
infra/core/search/bing_custom_grounding.bicep
```

They are conditionally deployed when their corresponding dependent-resource types are configured.

Conceptually:

```text
Foundry Project
      |
      +--> Bing Grounding
      |
      +--> Bing Custom Grounding
```

These are template-supported capabilities rather than resources claimed as part of the validated base deployment.

---

## 15. Connection Architecture

Foundry project connections are represented as infrastructure.

The centralized connection module is:

```text
infra/core/ai/connection.bicep
```

The AI project template can iterate through connection configuration and create project connections.

Conceptually:

```text
Supporting Azure Resource
          |
          v
Foundry Connection Resource
          |
          v
Foundry Project
```

This allows external resource integration to remain declarative rather than being configured manually after deployment.

---

## 16. Identity Architecture

The architecture uses multiple system-assigned identities.

```text
Foundry AI Account
        |
        +--> System-Assigned Managed Identity

Foundry Project
        |
        +--> System-Assigned Managed Identity
```

Managed identities provide Azure-managed identities for resources without embedding credentials directly into application or infrastructure source files.

---

## 17. RBAC Architecture

The deployment includes Azure role assignments for the principal performing the lab deployment.

Conceptually:

```text
Deployment Principal
        |
        +--> Foundry User
        |
        +--> Azure AI Developer
        |
        +--> Cognitive Services User
```

Role scopes differ according to their purpose.

The project identity also receives Foundry-related access at the AI account scope.

This architecture demonstrates role-based authorization rather than embedding static Azure credentials into the Bicep templates.

---

## 18. Optional GitHub Actions Identity

The AI project template defines:

```text
githubActionsPrincipalId
```

as an optional parameter.

If supplied, the infrastructure can grant the corresponding service principal Foundry access.

Conceptually:

```text
GitHub Actions
      |
      v
Azure Service Principal
      |
      v
Foundry RBAC
      |
      v
Foundry Project API
```

This creates an infrastructure path for later CI/CD and automated evaluation workflows.

The parameter existing in the template does not mean GitHub Actions authentication was configured as part of this base project.

---

## 19. Parameter Flow

Infrastructure configuration flows through several layers:

```text
AZD Environment
      |
      v
main.parameters.json
      |
      v
main.bicep
      |
      v
ai-project.bicep
      |
      v
Individual Resource Modules
```

Examples of AZD-provided values include:

```text
AZURE_ENV_NAME
AZURE_RESOURCE_GROUP
AZURE_LOCATION
AZURE_AI_ACCOUNT_NAME
AZURE_AI_PROJECT_NAME
AZURE_PRINCIPAL_ID
AZURE_PRINCIPAL_TYPE
ENABLE_MONITORING
ENABLE_HOSTED_AGENTS
```

This separates deployment configuration from reusable infrastructure code.

---

## 20. Infrastructure Outputs

The Bicep architecture exposes deployment outputs for use by applications, tooling, or later deployment stages.

These include values representing:

```text
Resource Group
Foundry AI Account
Foundry Project
Foundry Project Endpoint
Azure OpenAI Endpoint
Application Insights Connection String
Model Deployment Names
Container Registry Information
Optional Dependent Resource Information
```

Optional-resource outputs resolve according to whether those dependencies were provisioned.

Sensitive output values should not be committed to source control.

---

## 21. Local AZD State

Azure Developer CLI maintains local environment state under:

```text
.azure/
```

This directory may contain environment-specific deployment metadata and is intentionally excluded from the portfolio repository.

The portfolio repository also excludes:

```text
.env
```

while providing:

```text
.env.example
```

with placeholder values.

---

## 22. Security Model

Security-relevant characteristics implemented in the current architecture include:

```text
System-Assigned Managed Identity
Azure RBAC
Local AI Account Authentication Disabled
Environment-Based Configuration
No Embedded Azure Passwords
No Embedded Access Tokens
No Embedded API Keys in Portfolio Configuration
```

The connection module architecture contains a path for API-key-based connections, but keys should be supplied through secure parameters or a secrets-management system rather than committed to source control.

---

## 23. Network Security Boundary

The current AI account configuration uses:

```text
publicNetworkAccess = Enabled
defaultAction       = Allow
```

with no configured virtual-network or IP restrictions in the base template.

Therefore this project should not be represented as implementing private networking.

Potential production hardening could include:

```text
Private Endpoints
Restricted Network ACLs
VNet Integration
Azure Private DNS
Azure Firewall / Controlled Egress
Azure Policy
```

These are future enhancements, not current implementation claims.

---

## 24. Deployment Lifecycle

The normal infrastructure lifecycle is:

```text
Authenticate
    |
    v
Configure AZD Environment
    |
    v
azd up
    |
    v
Bicep Evaluation
    |
    v
Azure Resource Deployment
    |
    v
Foundry Project Configuration
    |
    v
Project Connections
    |
    v
Deployment Outputs
```

Because Azure resource operations are asynchronous, resource-state conflicts can occasionally occur during complex provisioning.

---

## 25. Deployment Troubleshooting Observed

Two Azure lifecycle scenarios were encountered during the completed infrastructure deployment.

### Soft-Deleted AI Services Resource

An earlier AI Services resource remained in Azure's soft-deleted state.

Attempting to recreate the resource with the same identity resulted in a restore-related deployment error.

The deleted resource was identified, purged, and the deployment was retried.

### Concurrent Azure Resource Operation

A subsequent deployment encountered:

```text
RequestConflict
```

while another Azure operation was still processing against the Foundry resource.

After the existing operation completed, rerunning the declarative deployment allowed provisioning to finish successfully.

These scenarios highlight practical infrastructure concerns involving:

```text
Soft deletion
Azure resource lifecycle state
Asynchronous provisioning
Deployment retries
Declarative reconciliation
```

---

## 26. Validated Deployment

The successful `azd up` execution provisioned:

```text
rg-dev-trail-guide
        |
        +--> Microsoft Foundry AI Account
        |        |
        |        +--> Foundry Project
        |        |
        |        +--> gpt-5-mini
        |        |
        |        +--> agents Capability Host
        |
        +--> Log Analytics Workspace
        |
        +--> Application Insights
        |
        +--> Azure Container Registry
```

The Foundry project also received connections for:

```text
Application Insights
Azure Container Registry
```

Environment-specific generated resource names are not required for reproducing the architecture because the Bicep templates derive names from deployment parameters and resource tokens.

---

## 27. Repository Architecture

```text
10-genaiops-foundry-infrastructure/
│
├── azure.yaml
│
├── infra/
│   ├── main.bicep
│   ├── main.parameters.json
│   ├── abbreviations.json
│   │
│   └── core/
│       ├── ai/
│       │   ├── ai-project.bicep
│       │   └── connection.bicep
│       │
│       ├── host/
│       │   └── acr.bicep
│       │
│       ├── monitor/
│       │   ├── applicationinsights.bicep
│       │   ├── applicationinsights-dashboard.bicep
│       │   └── loganalytics.bicep
│       │
│       ├── search/
│       │   ├── azure_ai_search.bicep
│       │   ├── bing_grounding.bicep
│       │   └── bing_custom_grounding.bicep
│       │
│       └── storage/
│           └── storage.bicep
│
├── docs/
│   └── architecture.md
│
├── .env.example
├── .gitignore
└── README.md
```

---

## 28. GenAIOps Position

This project represents the infrastructure stage of the broader GenAIOps lifecycle.

```text
Infrastructure Provisioning
          |
          v
Prompt / Agent Development
          |
          v
Evaluation
          |
          v
Automated Quality Gates
          |
          v
Deployment
          |
          v
Monitoring / Tracing
          |
          v
Optimization
```

Project #10 focuses specifically on the first layer:

```text
Infrastructure Provisioning
```

Later GenAIOps projects can build evaluation, CI/CD, monitoring, tracing, and optimization capabilities on top of this foundation.

---

## 29. Architectural Boundaries

Implemented or directly supported by the validated infrastructure:

```text
Azure Developer CLI orchestration
Bicep Infrastructure as Code
Foundry AI account
Foundry project
Model deployment
Managed identities
RBAC
Hosted-agent capability host
Application Insights
Log Analytics
Azure Container Registry
Foundry project connections
Conditional infrastructure modules
```

Not claimed as implemented by this project:

```text
Private networking
Production-grade secrets management
Automated evaluation pipeline
Prompt versioning pipeline
AI quality gates
Complete CI/CD deployment pipeline
Fine-tuning
Automated rollback
Multi-environment promotion
Infrastructure drift monitoring
Application-level distributed tracing
```

This separation prevents infrastructure capabilities present in the source template from being confused with functionality actually exercised during the completed module.

---

## 30. Engineering Takeaway

The primary engineering pattern demonstrated is:

```text
Declarative Configuration
        +
Modular Infrastructure as Code
        +
Managed Identity / RBAC
        +
Conditional Dependencies
        +
Observability Foundation
        =
Reusable Microsoft Foundry Platform
```

This establishes a repeatable Azure platform foundation on which more advanced GenAIOps capabilities can be developed.
