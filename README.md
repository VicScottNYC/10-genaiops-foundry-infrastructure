# GenAIOps Microsoft Foundry Infrastructure

A modular Infrastructure as Code project for provisioning a Microsoft Foundry environment using **Azure Developer CLI (azd)** and **Bicep**.

This project demonstrates repeatable AI platform provisioning, model deployment, identity and RBAC configuration, hosted-agent infrastructure, observability integration, and extensible dependent-resource architecture.

## Project Overview

Generative AI engineering extends beyond building prompts and agents.

Production-oriented AI environments also require repeatable infrastructure for:

- AI platform resources
- Projects
- Model deployments
- Identity
- Role-based access control
- Monitoring
- Hosted-agent capabilities
- Supporting Azure services
- Resource connections

This project addresses that infrastructure layer using:

```text
Azure Developer CLI
        +
      Bicep
        |
        v
Microsoft Foundry Infrastructure
```

The deployment is initiated with:

```bash
azd up
```

Azure Developer CLI uses `azure.yaml` to locate the Bicep infrastructure and orchestrate provisioning.

---

## Engineering Competency

The primary competency demonstrated by this project is:

> Microsoft Foundry platform provisioning through Azure Developer CLI and modular Bicep Infrastructure as Code.

The implementation includes:

- Subscription-scoped Bicep orchestration
- Resource-group provisioning
- Microsoft Foundry account provisioning
- Microsoft Foundry project provisioning
- Azure OpenAI model deployment
- System-assigned managed identities
- Azure RBAC assignments
- Hosted-agent capability infrastructure
- Application Insights
- Log Analytics
- Azure Container Registry integration
- Foundry project connections
- Parameterized deployment
- Conditional infrastructure modules
- Environment-based configuration
- Reusable Bicep modules

---

## Architecture

The deployed architecture can be represented as:

```text
Developer Workstation
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
        +------------------------------+
        |                              |
        v                              v
Resource Group                 AI Project Module
                                       |
                 +---------------------+--------------------+
                 |                     |                    |
                 v                     v                    v
        Foundry AI Account      Foundry Project      Model Deployment
                 |                     |               gpt-5-mini
                 |                     |
                 |                     +---------------------+
                 |                                           |
                 v                                           v
        Capability Host                              Project Connections
          "agents"
                 |
                 v
        Hosted-Agent Support

        Observability
        ┌────────────────────┐
        │ Log Analytics      │
        │ Application        │
        │ Insights           │
        └────────────────────┘

        Supporting Infrastructure
        ┌────────────────────┐
        │ Container Registry │
        └────────────────────┘
```

Additional dependent-resource modules exist in the infrastructure architecture and can be conditionally enabled through configuration.

---

## Successfully Provisioned Infrastructure

During validation of this project, `azd up` successfully provisioned the following infrastructure:

```text
Resource Group
Microsoft Foundry AI Account
Microsoft Foundry Project
gpt-5-mini Model Deployment
Foundry Capability Host
Application Insights
Log Analytics Workspace
Azure Container Registry
Application Insights Project Connection
Azure Container Registry Project Connection
```

This represents the infrastructure actually exercised during the completed deployment.

---

## Azure Developer CLI

The project uses Azure Developer CLI as the deployment entry point.

`azure.yaml` specifies:

```yaml
infra:
  provider: bicep
  path: ./infra
```

This tells `azd` to use the Bicep templates contained in the `infra/` directory.

The configuration also requires the Azure AI Agents extension:

```yaml
requiredVersions:
  extensions:
    "azure.ai.agents": ">=0.1.0-preview"
```

The resulting deployment workflow is:

```text
azd up
   |
   v
Read azure.yaml
   |
   v
Resolve AZD environment
   |
   v
Evaluate Bicep parameters
   |
   v
Provision Azure resources
   |
   v
Expose deployment outputs
```

---

## Infrastructure as Code

The root Bicep template is:

```text
infra/main.bicep
```

It operates at subscription scope:

```bicep
targetScope = 'subscription'
```

The template creates or targets the resource group and delegates Foundry infrastructure creation to the modular AI project template:

```text
infra/core/ai/ai-project.bicep
```

This creates a layered architecture:

```text
main.bicep
    |
    v
Resource Group
    |
    v
ai-project.bicep
    |
    +-- AI Account
    +-- Foundry Project
    +-- Model Deployments
    +-- Identity / RBAC
    +-- Monitoring
    +-- Capability Host
    +-- Resource Connections
    +-- Conditional Dependencies
```

---

## Microsoft Foundry Account

The infrastructure provisions a Microsoft Cognitive Services account configured as:

```bicep
kind: 'AIServices'
sku: {
  name: 'S0'
}
```

The account is configured with a system-assigned managed identity:

```bicep
identity: {
  type: 'SystemAssigned'
}
```

Project management is enabled:

```bicep
allowProjectManagement: true
```

Local authentication is disabled:

```bicep
disableLocalAuth: true
```

This shifts authentication toward Microsoft Entra ID and Azure RBAC rather than relying on local account keys.

---

## Microsoft Foundry Project

The Bicep architecture provisions the Foundry project as a child of the AI account:

```text
Microsoft.CognitiveServices/accounts/projects
```

The project also receives a system-assigned managed identity.

Conceptually:

```text
Foundry AI Account
       |
       v
Foundry Project
       |
       v
Project Managed Identity
```

This identity can participate in Azure RBAC-based access to resources required by the project.

---

## Model Deployment

The infrastructure defines model deployments declaratively.

The root template configures:

```text
gpt-5-mini
```

using an OpenAI model deployment.

The Bicep implementation iterates through the configured deployment collection:

```text
deployments
    |
    v
Microsoft.CognitiveServices/accounts/deployments
```

Each configured model becomes an Azure resource deployment under the AI account.

The deployment logic uses:

```bicep
@batchSize(1)
```

so model deployments are processed one at a time, helping reduce capacity conflicts.

---

## Hosted-Agent Infrastructure

Hosted-agent support is controlled by:

```text
enableHostedAgents
```

When enabled, the infrastructure creates a Foundry capability host:

```text
Microsoft.CognitiveServices/accounts/capabilityHosts
```

with:

```text
capabilityHostKind: Agents
```

The capability host uses the name:

```text
agents
```

The implementation enables the public hosting environment when the hosted-agent capability is provisioned.

---

## Observability

Monitoring is controlled by:

```text
enableMonitoring
```

which defaults to:

```text
true
```

When enabled, the infrastructure provisions:

```text
Log Analytics Workspace
        |
        v
Application Insights
        |
        v
Foundry Project Connection
```

Application Insights is connected to the Log Analytics workspace.

A project connection is then created so the Foundry project can reference the Application Insights resource.

This establishes the infrastructure foundation for later GenAIOps monitoring and tracing workflows.

---

## Identity and RBAC

The infrastructure assigns Azure roles rather than depending solely on embedded credentials.

The deploying principal receives role assignments that support Foundry and Cognitive Services operations.

The architecture includes:

```text
Deploying Principal
       |
       +--> Foundry User
       |
       +--> Azure AI Developer
       |
       +--> Cognitive Services User
```

The Foundry project identity also receives a Foundry-related role assignment at the AI account scope.

An optional GitHub Actions service-principal parameter is available:

```text
githubActionsPrincipalId
```

When populated, the template can assign the required Foundry role to that service principal for CI/CD-oriented workflows.

That capability exists in the template but was not required to demonstrate the initial infrastructure deployment.

---

## Azure Container Registry

When hosted-agent deployment is enabled and a registry dependency is required, the root architecture adds:

```text
registry
```

as a dependent resource.

The ACR module provisions the registry and establishes the associated Foundry project connection.

Conceptually:

```text
Hosted Agents Enabled
        |
        v
Registry Dependency
        |
        v
Azure Container Registry
        |
        v
Foundry Project Connection
```

The successful validation deployment provisioned both the registry and its project connection.

---

## Conditional Infrastructure

The architecture supports additional resources that are created only when requested through configuration.

Supported dependent-resource types include:

```text
storage
registry
azure_ai_search
bing_grounding
bing_custom_grounding
```

These map to reusable modules under:

```text
infra/core/
```

The presence of these modules demonstrates an extensible IaC architecture.

They should not be interpreted as resources automatically deployed in every environment.

---

## Optional Storage Integration

The template includes:

```text
infra/core/storage/storage.bicep
```

Storage is provisioned only when a storage dependency is configured.

The architecture can then create the corresponding project connection.

---

## Optional Azure AI Search Integration

The template includes:

```text
infra/core/search/azure_ai_search.bicep
```

Azure AI Search is provisioned only when the corresponding dependency is configured.

The module can also receive the storage resource ID when storage is enabled.

This provides an infrastructure foundation for knowledge-grounded AI architectures.

---

## Optional Grounding Resources

The template contains conditional modules for:

```text
Bing Grounding
Bing Custom Grounding
```

These resources are created only when their corresponding dependencies are configured.

They are template-supported capabilities and were not required for the validated base deployment.

---

## Project Connections

Foundry project connections are treated as infrastructure resources.

The architecture includes a centralized connection module:

```text
infra/core/ai/connection.bicep
```

Resource modules can establish connections between the Foundry project and supporting Azure resources.

Examples represented by the architecture include:

```text
Application Insights
Azure Container Registry
Storage
Azure AI Search
Bing Grounding
Bing Custom Grounding
```

This allows external platform dependencies to be represented declaratively alongside the Foundry project.

---

## Parameterization

Deployment values are supplied through:

```text
infra/main.parameters.json
```

The parameter file maps Azure Developer CLI environment variables to Bicep parameters.

Examples include:

```text
AZURE_RESOURCE_GROUP
AZURE_ENV_NAME
AZURE_LOCATION
AZURE_AI_ACCOUNT_NAME
AZURE_AI_PROJECT_NAME
AZURE_PRINCIPAL_ID
AZURE_PRINCIPAL_TYPE
ENABLE_MONITORING
ENABLE_HOSTED_AGENTS
```

This separates environment-specific configuration from the infrastructure implementation.

---

## Environment Management

Azure Developer CLI maintains local deployment state under:

```text
.azure/
```

That directory is intentionally excluded from this portfolio repository.

Local deployment values may also be exported to:

```text
.env
```

The real `.env` file is excluded from Git.

The repository provides:

```text
.env.example
```

containing placeholders only.

---

## Project Structure

```text
10-genaiops-foundry-infrastructure/
├── .env.example
├── .gitignore
├── README.md
├── azure.yaml
├── infra/
│   ├── abbreviations.json
│   ├── main.bicep
│   ├── main.parameters.json
│   └── core/
│       ├── ai/
│       │   ├── ai-project.bicep
│       │   └── connection.bicep
│       ├── host/
│       │   └── acr.bicep
│       ├── monitor/
│       │   ├── applicationinsights-dashboard.bicep
│       │   ├── applicationinsights.bicep
│       │   └── loganalytics.bicep
│       ├── search/
│       │   ├── azure_ai_search.bicep
│       │   ├── bing_custom_grounding.bicep
│       │   └── bing_grounding.bicep
│       └── storage/
│           └── storage.bicep
└── docs/
    └── architecture.md
```

---

## Prerequisites

The deployment requires:

- Azure subscription
- Azure CLI
- Azure Developer CLI
- Appropriate Azure permissions
- Access to Microsoft Foundry
- Azure AI Agents AZD extension
- Model availability in the selected Azure region

Model availability and Azure capacity can vary by region and subscription.

---

## Authentication

Authenticate to Azure before provisioning:

```bash
az login
```

Azure Developer CLI may also require authentication:

```bash
azd auth login
```

No Azure passwords, API keys, or access tokens should be committed to this repository.

---

## Deployment

Create or select an Azure Developer CLI environment and deploy:

```bash
azd up
```

AZD resolves the environment parameters and provisions the Bicep infrastructure.

The deployment is designed to be declarative: subsequent executions reconcile the desired infrastructure state with Azure.

---

## Deployment Validation

The infrastructure was validated through a successful `azd up` execution.

The completed deployment included:

```text
Resource Group
Foundry AI Account
gpt-5-mini Model Deployment
Log Analytics Workspace
Foundry Project
Application Insights
Foundry Capability Host
Application Insights Project Connection
Azure Container Registry
Azure Container Registry Project Connection
```

A transient Azure `RequestConflict` occurred while the Foundry resource was still processing an earlier operation. Re-running the declarative deployment after the Azure operation completed allowed provisioning to finish successfully.

A separate earlier deployment was blocked by a soft-deleted AI Services resource. The stale resource was identified and purged before the deployment was retried.

These scenarios demonstrate practical Azure infrastructure lifecycle considerations around soft deletion, resource-state conflicts, and idempotent deployment retries.

---

## Security Considerations

The project incorporates several security practices:

- `.env` excluded from source control
- `.azure/` local deployment state excluded
- System-assigned managed identities
- Azure RBAC role assignments
- Local authentication disabled on the AI account
- Environment-based configuration
- No embedded Azure credentials in the Bicep templates
- Optional service-principal RBAC for automation

The base template currently enables public network access for the AI account.

Production environments may require additional controls such as:

- Private endpoints
- Restricted network ACLs
- Azure Key Vault
- Managed identity for hosted workloads
- Least-privilege RBAC review
- Azure Policy
- Resource locks
- Diagnostic retention policies

Those controls are potential production enhancements rather than capabilities claimed by this implementation.

---

## Infrastructure Modules

### AI

```text
infra/core/ai/ai-project.bicep
infra/core/ai/connection.bicep
```

Responsible for the Foundry account/project architecture, model deployments, identities, RBAC, connections, monitoring integration, and conditional dependent resources.

### Hosted-Agent Infrastructure

```text
infra/core/host/acr.bicep
```

Provides Azure Container Registry infrastructure and project integration when required.

### Monitoring

```text
infra/core/monitor/applicationinsights.bicep
infra/core/monitor/applicationinsights-dashboard.bicep
infra/core/monitor/loganalytics.bicep
```

Provides the observability infrastructure used by the Foundry environment.

### Search and Grounding

```text
infra/core/search/azure_ai_search.bicep
infra/core/search/bing_grounding.bicep
infra/core/search/bing_custom_grounding.bicep
```

Provides optional infrastructure modules for search and grounding scenarios.

### Storage

```text
infra/core/storage/storage.bicep
```

Provides optional storage infrastructure and Foundry project connectivity.

---

## GenAIOps Context

GenAIOps applies software-engineering and operational disciplines to generative AI systems.

This project focuses on the **infrastructure foundation** of that lifecycle:

```text
GenAIOps
   |
   +--> Infrastructure as Code       <-- Project #10
   |
   +--> Prompt management
   |
   +--> Evaluation
   |
   +--> CI/CD
   |
   +--> Monitoring and tracing
   |
   +--> Optimization
```

Later stages can build on the infrastructure established here.

This repository intentionally does not claim to implement evaluation pipelines, prompt versioning, automated AI quality gates, fine-tuning, or complete GenAIOps CI/CD.

---

## Portfolio Progression

This is **Project #10** in a Microsoft Foundry and Azure AI engineering portfolio.

Projects #01–#09 primarily established application and agent engineering competencies.

Project #10 introduces the infrastructure layer:

```text
AI Application Engineering
          |
          v
Agent Engineering
          |
          v
Knowledge + MCP
          |
          v
Multi-Agent Orchestration
          |
          v
Infrastructure as Code
          |
          v
GenAIOps / AI Platform Engineering
```

The key new competency is:

> **Repeatable provisioning of a Microsoft Foundry environment using Azure Developer CLI and modular Bicep Infrastructure as Code.**

---

## Future Enhancements

Potential extensions include:

- Private networking
- Private endpoints
- Azure Key Vault integration
- Additional Azure Policy controls
- Deployment validation tests
- Bicep linting in CI
- GitHub Actions deployment workflow
- Federated GitHub-to-Azure authentication
- Automated AI evaluation workflows
- GenAIOps quality gates
- Prompt versioning
- Monitoring dashboards
- Distributed tracing
- Production alerting
- Environment promotion across development, test, and production
- Infrastructure drift detection

---

## Implementation Boundaries

This repository demonstrates the infrastructure provisioning layer.

It does not by itself implement:

```text
AI application business logic
Prompt evaluation pipelines
Agent evaluation pipelines
Fine-tuning workflows
Complete CI/CD pipelines
Production private networking
Automated rollback
Multi-environment promotion
```

Those capabilities belong to later stages of the GenAIOps lifecycle.

---

## Training Context

The initial infrastructure was developed while completing the Microsoft GenAIOps infrastructure setup exercise for Microsoft Foundry.

The portfolio version isolates the deployable Infrastructure as Code and documents the engineering architecture independently from the broader training repository.

---

## Summary

Project #10 establishes the infrastructure foundation required for more mature GenAIOps workflows.

It demonstrates:

```text
Azure Developer CLI
        +
Modular Bicep
        +
Microsoft Foundry
        +
Model Deployment
        +
Managed Identity / RBAC
        +
Hosted-Agent Infrastructure
        +
Observability
        +
Conditional Azure Dependencies
```

The result is a reusable, parameterized Microsoft Foundry infrastructure architecture that can serve as the platform foundation for subsequent generative AI development and operational workflows.


## Module 10 Exercises 1–6

The [exercise archive and verification checklist](module10/README.md) includes agent prompts, evaluation code and datasets, monitoring scripts, and completed fine-tuning simulation transcripts. See the checklist for evidence gaps.
