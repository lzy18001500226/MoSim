import { Button } from "@/components/ui/button";
import type { TranslationFn } from "./GeneralSettings";
import type { OrganizationMember } from "@/lib/api/facade/org";

interface MembersListProps {
  members: OrganizationMember[];
  loading: boolean;
  currentUserId?: number;
  t: TranslationFn;
  onRoleChange: (userId: number, newRole: string) => void;
  onRemove: (userId: number) => void;
}

export function MembersList({ members, loading, currentUserId, t, onRoleChange, onRemove }: MembersListProps) {
  if (loading) {
    return <div className="text-center py-8 text-muted-foreground">{t("settings.members.loading")}</div>;
  }

  if (members.length === 0) {
    return <div className="text-center py-8 text-muted-foreground">{t("settings.members.noMembers")}</div>;
  }

  return (
    <div className="space-y-3">
      {members.map((member) => {
        const userId = Number(member.userId);
        return (
        <div key={userId || Number(member.id)} className="flex items-center justify-between p-4 border border-border rounded-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center text-sm font-medium">
              {member.user?.name?.[0] || member.user?.username?.[0] || "?"}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-medium">
                  {member.user?.name || member.user?.username || "Unknown"}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${getRoleBadgeColor(member.role)}`}>
                  {member.role}
                </span>
                {userId === currentUserId && (
                  <span className="text-xs text-muted-foreground">{t("settings.members.you")}</span>
                )}
              </div>
              <p className="text-sm text-muted-foreground">{member.user?.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {member.role !== "owner" && userId !== currentUserId && (
              <>
                <select
                  value={member.role}
                  onChange={(e) => onRoleChange(userId, e.target.value)}
                  className="text-sm border border-border rounded px-2 py-1 bg-background"
                >
                  <option value="member">{t("settings.members.roleMember")}</option>
                  <option value="admin">{t("settings.members.roleAdmin")}</option>
                </select>
                <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive"
                  onClick={() => onRemove(userId)}>
                  {t("settings.members.remove")}
                </Button>
              </>
            )}
          </div>
        </div>
      );
      })}
    </div>
  );
}

function getRoleBadgeColor(role: string) {
  switch (role) {
    case "owner": return "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400";
    case "admin": return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
    default: return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300";
  }
}
