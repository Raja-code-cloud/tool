/** Permission and role checks aligned with backend RBAC. */

export function hasPermission(permissions: readonly string[], required: string): boolean {
  return permissions.some((permission) => {
    if (permission === "*" || permission === required) return true;
    if (permission.endsWith(":*")) {
      const namespace = permission.slice(0, -2);
      return required.startsWith(`${namespace}:`);
    }
    return false;
  });
}

export function hasRole(roles: readonly string[], role: string): boolean {
  return roles.includes(role);
}

export function formatRoleLabel(roles: readonly string[]): string {
  if (roles.includes("admin")) return "Administrator";
  if (roles.includes("editor")) return "Editor";
  if (roles.includes("user")) return "Member";
  return roles[0] ?? "Member";
}
