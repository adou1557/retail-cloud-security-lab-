# **AZ-305 Architecture Study Notes — Week 1: Identity, Governance & Access Design**

Comprehensive architectural reference, decision trees, and exam patterns for Microsoft Entra ID hybrid topologies, workload identities, and cryptographic key management.

# **1\. Hybrid Identity Architecture: Entra Connect vs. Entra Cloud Sync**

Designing hybrid identity requires balancing synchronization capabilities, on-premises operational overhead, and multi-forest network topologies.

## **1.1 Technical Comparison Matrix**

| Evaluation Criteria | Microsoft Entra Connect (Classic Sync Engine) | Microsoft Entra Cloud Sync (Lightweight Agent) |
| :---- | :---- | :---- |
| **Architecture & Footprint** | Heavy server-side engine running locally; requires SQL Server (LocalDB or dedicated SQL instance). Synchronization processing occurs on-premises. | Lightweight agent footprint (approx. 200–300 MB); synchronization computation and scheduling execute natively in the Azure Cloud. |
| **High Availability (HA)** | Active / Staging architecture. Complex manual failover process requiring state export and staging mode toggle. | Multi-agent active deployment. Out-of-the-box automatic load balancing and failover across up to 40 agents per tenant. |
| **Network & Forest Topologies** | Requires direct line-of-sight (VPN / ExpressRoute) between all AD forests and the centralized sync server. | Supports fully disconnected, isolated, non-routable AD forests (ideal for M\&A scenarios). |
| **Attribute Transformation** | Deep customization via the Synchronization Rules Editor and advanced custom sync expressions. | Declarative attribute mapping using standard schema attributes and simple expressions. |
| **Supported Workloads** | Device writeback (hybrid Azure AD join), Exchange hybrid writeback, user writeback, large security groups (\>50k members). | Primary focus on users, contacts, and security groups. No device writeback or Exchange hybrid deployment support. |
| **Authentication Methods** | Password Hash Sync (PHS), Pass-Through Authentication (PTA), and Active Directory Federation Services (AD FS). | Password Hash Sync (PHS). Integrates with existing federation, but cannot deploy PTA independently. |

## **1.2 Decision Rules for Enterprise Design (AZ-305 Triggers)**

* **Select Microsoft Entra Cloud Sync when:**  
  * The scenario requires synchronizing identities across disconnected Active Directory forests (e.g., corporate acquisitions) without establishing site-to-site VPNs, ExpressRoute, or AD forest trusts.  
  * The objective is zero on-premises database maintenance and rapid deployment of high-availability sync agents.  
  * Workload is restricted to standard user accounts, basic security groups, and password hash synchronization.  
* **Select Microsoft Entra Connect when:**  
  * Complex directory schema extensions or custom attribute transformations are mandatory.  
  * The business requires device synchronization (Hybrid Azure AD Join / Intune co-management).  
  * Exchange hybrid deployment with mailbox cross-premises writeback is deployed.  
  * Existing on-premises AD FS requires direct lifecycle and claim rule alignment.

# **2\. Workload & Application Identities: Managed Identities vs. Service Principals**

A zero-trust identity plane eliminates hardcoded credentials, long-lived client secrets, and certificate renewal operational overhead.

## **2.1 Identity Selection Workflow**

Workload requires access to Azure Resources

 ├── Is workload hosted on Azure Compute?

 │    ├── NO  \-\> Use App Registration / Service Principal

 │    │          └─ Store secret/cert in Key Vault; rotate via automated pipeline.

 │    │

 │    └── YES \-\> Are permissions shared across multiple homogeneous resources?

 │                 ├── YES \-\> User-Assigned Managed Identity

 │                 │          └─ Decoupled lifecycle, shared across VMSS/pools.

 │                 │

 │                 └── NO  \-\> System-Assigned Managed Identity

 │                            └─ 1:1 lifecycle bound to resource, auto-deleted.

## **2.2 System-Assigned vs. User-Assigned Managed Identities**

| Feature | System-Assigned Managed Identity | User-Assigned Managed Identity |
| :---- | :---- | :---- |
| **Lifecycle** | Strictly tied to the parent Azure resource. When the resource is deleted, Azure deletes the identity automatically in Entra ID. | Independent standalone lifecycle. Exists as an Azure resource in a resource group; deleted only via deliberate administrator action. |
| **Sharing** | Cannot be shared across resources. One resource maps to exactly one system identity. | Can be assigned to multiple Azure resources (e.g., across an entire VM Scale Set or fleet of microservices). |
| **Provisioning** | Enabled directly via resource configuration flag (`identity.type = "SystemAssigned"`). | Created first (`Microsoft.ManagedIdentity/userAssignedIdentities`), then attached to target compute resources. |
| **Best Architectural Fit** | Single-purpose workloads (e.g., dedicated Azure Function auditing storage, single VM accessing a specific database). | Multi-instance workloads, blue/green deployments, or container node pools sharing identical downstream RBAC permissions. |

# **3\. Secret, Key, and Certificate Management: Azure Key Vault Architecture**

## **3.1 Permission Models: Azure RBAC vs. Vault Access Policies**

| Attribute | Azure RBAC Model (Recommended) | Vault Access Policy (Legacy) |
| :---- | :---- | :---- |
| **Scope Granularity** | Subscription, Resource Group, Vault, or individual Key / Secret / Certificate level. | Vault-wide only (all-or-nothing for secrets, keys, or certs inside the vault). |
| **Privileged Access Management** | Fully integrated with Microsoft Entra Privileged Identity Management (PIM) for just-in-time (JIT) access. | Incompatible with PIM elevation at the granular secret level. |
| **Role Separation** | Predefined native roles: Key Vault Administrator, Key Vault Secrets User, Key Vault Crypto Officer, Key Vault Reader. | Requires custom matrix of GET/LIST/SET permissions manually maintained per principal. |

## **3.2 SKU Tiering: Standard vs. Premium vs. Managed HSM**

* **Key Vault Standard:** Multi-tenant HSM partition. Software-protected keys and secrets. FIPS 140-2 Level 2 validated.  
* **Key Vault Premium:** Multi-tenant HSM partition. Hardware-protected keys (HSM-backed). FIPS 140-2 Level 3 validated.  
* **Azure Key Vault Managed HSM:**  
  * Single-tenant, fully managed, highly available HSM cluster dedicated to a single customer.  
  * FIPS 140-2 Level 3 validated hardware.  
  * Customer-controlled security domain (data isolation).  
  * Enforces localized RBAC decoupled from Azure subscription management planes.  
  * Mandatory for high-security regulatory compliance (financial services, payment gateways, defense workloads).

## **3.3 Data Resilience & Anti-Ransomware Baselines**

* **Soft Delete:** Retains deleted vaults and vault objects for a configurable retention window (7 to 90 days; 90 days default). Protects against accidental deletion.  
* **Purge Protection:** Prevents premature permanent deletion of soft-deleted items until the full retention duration elapses.  
* **Architectural Rule:** In production environments, always enforce `enableSoftDelete: true` and `enablePurgeProtection: true` via Azure Policy to defeat ransomware and rogue administrator sabotage.

# **4\. Privileged Access & Conditional Access Design**

## **4.1 Entra ID Privileged Identity Management (PIM)**

* **Just-In-Time (JIT) Activation:** Eliminates permanent standing admin access.  
* **Time-Bound Assignments:** Maximum activation duration (e.g., 8 hours).  
* **Mandatory Controls on Elevation:**  
  * Multi-Factor Authentication (MFA) enforcement upon role activation.  
  * Justification ticket and business reason capture.  
  * Approval workflow requiring designated approvers for critical roles (Global Administrator, Privileged Role Administrator).  
* **Access Reviews:** Automated quarterly recertification of privileged roles and group memberships with auto-remediation (revoke if reviewer does not respond).

## **4.2 Conditional Access (CA) Architecture Patterns**

* **Zero-Trust Access Engine:** Evaluates Signals (User, Location, Device compliance, Client application, Risk score) \-\> Enforces Decision (Block, Allow with MFA, Require Intune Compliance, Session control).  
* **Break-Glass (Emergency Access) Accounts:**  
  * Minimum 2 cloud-only accounts excluded from all Conditional Access policies and MFA registration requirements.  
  * Monitored via dedicated Azure Monitor / Sentinel alert triggers whenever authentication occurs.  
* **Location Hardening:** Define Trusted Named Locations (VPN egress IPs) and block access originating from non-business sanctioned geographies.

# **5\. Architectural Decision Trees & AZ-305 Exam Traps**

## **5.1 Quick Reference Matrix: Identity Solutions**

| Business Requirement | Target Architectural Solution |
| :---- | :---- |
| Disconnected on-prem forests with zero VPN/ExpressRoute links | Microsoft Entra Cloud Sync |
| Hybrid Exchange mailbox writeback or device sync | Microsoft Entra Connect |
| Monitor health of on-premises AD FS infrastructure | Microsoft Entra Connect Health (requires Entra ID P1/P2) |
| Compute instances in a scale set need to read secrets | User-Assigned Managed Identity \+ Azure RBAC |
| Customer demands dedicated HSM hardware for cryptographic isolation | Azure Key Vault Managed HSM |
| Temporary privilege elevation with mandatory approval workflow | Microsoft Entra Privileged Identity Management (PIM) |
| External business partners need access to internal apps | Microsoft Entra External ID (B2B Collaboration) |
| Consumer-facing mobile app requires social login (Google/Apple) | Azure AD B2C / Entra External ID for Customers |

## **5.2 Top Exam Traps**

* **Managed Identity Scope:** Managed Identities can only access resources that support Microsoft Entra authentication (e.g., Azure SQL, Key Vault, Storage). For third-party SaaS APIs, use Key Vault to store secrets and retrieve them via a Managed Identity.  
* **Access Policy vs. RBAC Confusion:** If a case study asks to delegate permissions to read a single secret without granting visibility over the rest of the vault, choose Azure RBAC permission model (Key Vault Secrets User scoped to the secret). Vault Access Policies cannot scope permissions below the vault root.  
* **Emergency Access:** Never assign emergency break-glass accounts to specific humans; they must be generic, cloud-only initial domain accounts, with password stored in a secure physical safe, and excluded from all Conditional Access rules.

