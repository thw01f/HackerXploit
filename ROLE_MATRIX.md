# Role & Permissions Matrix

| Capability / Action | `root_admin` | `admin` | `teacher` | `member` |
| :--- | :---: | :---: | :---: | :---: |
| **Max Concurrent Users** | Exactly 1 | Max 5 (Hard Cap) | Unlimited | Unlimited |
| **Promote/Demote Admins** | ✅ | ❌ | ❌ | ❌ |
| **Transfer Root Status** | ✅ | ❌ | ❌ | ❌ |
| **Approve / Suspend / Reject Registrations** | ✅ | ✅ | ✅ | ❌ |
| **View All Members' Activity & Hours** | ✅ | ✅ | ✅ | ❌ |
| **View Audit Logs (`/api/admin/audit-logs`)** | ✅ | ✅ | ✅ | ❌ |
| **View Security Logs (`/admin/security/login-activity`)** | ✅ | ✅ | ❌ | ❌ |
| **System Backups & Retention Settings** | ✅ | ✅ | ❌ | ❌ |
| **Create Academy Courses & Lessons** | ✅ | ✅ | ✅ | ❌ |
| **Create Competitions** | Auto-Approved | Auto-Approved | Pending Admin | ❌ |
| **Verify Competition Applications** | ✅ | ✅ | ✅ | ❌ |
| **File Post-Event Wrap-ups** | ✅ | ✅ | ✅ | ❌ |
| **Moderate Chat Messages (Soft-Delete)** | ✅ | ✅ | ✅ | ❌ |
| **Wipe / Reset Chat Room (hard delete, `/api/chat/reset`)** | ✅ | ✅ | ❌ | ❌ |
| **Read Courses, Apply to Comps / Opps** | ✅ | ✅ | ✅ | ✅ |
| **Manage Own Profile & Device Sessions** | ✅ | ✅ | ✅ | ✅ |

---

## Key Invariants

1. **Root Admin Invariant**: Exactly one `root_admin` exists. Cannot be suspended or deleted by anyone.
2. **Admin Hard Cap**: Backend strictly rejects promoting a 6th user to `admin` role.
3. **Audit Log Invariant**: Every action taken by teachers or admins writes a non-repudiable entry to `audit_logs`.
