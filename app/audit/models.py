from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        EXPORT = "EXPORT", "Export"
        OTHER = "OTHER", "Other"

    created_at = models.DateTimeField(auto_now_add=True)

    # Who did it
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    # What happened
    action = models.CharField(max_length=20, choices=Action.choices, default=Action.OTHER)
    app_label = models.CharField(max_length=50, blank=True, default="")
    model_name = models.CharField(max_length=50, blank=True, default="")
    object_id = models.CharField(max_length=64, blank=True, default="")
    object_repr = models.CharField(max_length=255, blank=True, default="")

    # Details
    changes = models.JSONField(blank=True, null=True)  # store field diffs, payload, etc.
    message = models.TextField(blank=True, default="")

    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["action"]),
            models.Index(fields=["app_label", "model_name"]),
            models.Index(fields=["object_id"]),
        ]

    def __str__(self) -> str:
        who = getattr(self.user, "username", None) or "system"
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} | {who} | {self.action} | {self.app_label}.{self.model_name}#{self.object_id}"

