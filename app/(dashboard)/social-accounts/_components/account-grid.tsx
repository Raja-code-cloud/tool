import type { SocialAccount } from "@/lib/domain/social-account";

import { AccountCard, type AccountActions } from "./account-card";

export type AccountGridProps = {
  accounts: readonly SocialAccount[];
  comingSoon: readonly SocialAccount[];
  actions: AccountActions;
};

export function AccountGrid(props: AccountGridProps): React.JSX.Element {
  const renderCards = (accounts: readonly SocialAccount[]) =>
    accounts.map((account) => (
      <AccountCard key={account.id} account={account} actions={props.actions} />
    ));

  return (
    <div className="grid gap-6">
      {props.accounts.length > 0 && (
        <section aria-labelledby="connected-accounts-heading">
          <h2 id="connected-accounts-heading" className="text-heading-3 mb-4">
            Connected platforms
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {renderCards(props.accounts)}
          </div>
        </section>
      )}
      {props.comingSoon.length > 0 && (
        <section aria-labelledby="coming-soon-heading">
          <h2 id="coming-soon-heading" className="text-heading-3 mb-4">
            Coming soon
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {renderCards(props.comingSoon)}
          </div>
        </section>
      )}
    </div>
  );
}
