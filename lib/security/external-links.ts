/** Required rel tokens for external links opened in a new browsing context. */
export const EXTERNAL_LINK_REL = "noopener noreferrer" as const;

export type ExternalLinkRelProps = {
  readonly target: "_blank";
  readonly rel: typeof EXTERNAL_LINK_REL;
};

/** Returns safe attributes for external links. No external links exist today; use when adding them. */
export function externalLinkProps(): ExternalLinkRelProps {
  return { target: "_blank", rel: EXTERNAL_LINK_REL };
}
