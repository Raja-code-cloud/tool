# Frontend Release Process

## Preconditions

1. Merge the intended changes into `main`.
2. Confirm the latest Main Branch Build completed successfully.
3. Confirm the version does not already exist as a Git tag or GitHub release.
4. Choose a semantic version without a `v` prefix, such as `1.4.0` or
   `1.4.0-rc.1`.

## Create a release

1. Open **Actions > Release Frontend > Run workflow**.
2. Run the workflow from the trusted default branch.
3. Enter the semantic version.
4. Select prerelease for release candidates or preview releases.

The workflow always checks out `main`, validates the version, runs type checking,
linting, tests, and a production build, then updates package metadata inside the
ephemeral runner for packaging. It does not commit version changes.

## Outputs

After validation succeeds, the workflow:

- creates `cloud-content-hub-frontend-v<version>.tar.gz`;
- uploads the archive as a workflow artifact for 90 days;
- creates the `v<version>` Git tag at the validated `main` commit;
- generates release notes from GitHub's pull request and tag history;
- creates a GitHub release and attaches the archive.

The generated GitHub release notes are the release changelog.

## Production deployment

Treat the immutable release archive as the production deployment input. Connect
the release job to the selected hosting provider only after these controls exist:

- a protected GitHub `production` environment;
- required reviewer approval;
- provider credentials stored as environment secrets or exchanged through OIDC;
- deployment concurrency protection;
- health checks and a documented rollback procedure.

## Rollback

Redeploy a previously successful release artifact. Do not move or overwrite an
existing version tag. If code changes are required, revert through a pull
request, validate `main`, and issue a new patch release.

## Failed releases

Validation or packaging failures create neither a tag nor a release. If release
creation fails after packaging, inspect whether the tag or release was created
before rerunning. Resolve duplicate-version conflicts by selecting a new version;
do not delete published releases without explicit release-owner approval.
