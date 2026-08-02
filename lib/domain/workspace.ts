export type WorkspaceInfo = {
  readonly id?: string;
  readonly version?: number;
  readonly name: string;
  readonly shortName: string;
  readonly description: string;
  readonly timeZone?: string;
};

export type WorkspaceUser = {
  readonly name: string;
  readonly email: string;
  readonly role: string;
};
