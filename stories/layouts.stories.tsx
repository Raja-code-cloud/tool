import type { Meta, StoryObj } from "@storybook/react";

import {
  AppHeader,
  AppShell,
  Container,
  Navbar,
  PageContainer,
  PageHeader,
  PageTransition,
  SkipLink,
  Stack,
  TopNavbar,
  WorkspaceShell,
} from "../components/layout";
import { Button } from "../components/ui";

const meta = {
  title: "Layouts/Page Structure",
  component: Container,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component:
          "Responsive structural components define landmarks, page width, spacing, skip navigation, and application chrome without constraining feature content.",
      },
    },
  },
} satisfies Meta<typeof Container>;

export default meta;
type Story = StoryObj<typeof meta>;

export const ContainersAndStack: Story = {
  render: () => (
    <PageContainer>
      <Stack gap="lg">
        <PageHeader
          title="Campaigns"
          description="Plan and review content across channels."
          actions={<Button>Create</Button>}
        />
        <Container size="reading" className="bg-card rounded-lg border p-5">
          Reading-width content
        </Container>
      </Stack>
    </PageContainer>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "Container, PageContainer, Stack, and PageHeader adapt gutters, action wrapping, and readable line length at every viewport.",
      },
    },
  },
};

export const ApplicationShell: Story = {
  render: () => (
    <AppShell
      sidebar={<aside className="bg-card desktop:block hidden w-56 border-r p-4">Sidebar</aside>}
      header={<AppHeader title="Workspace" actions={<Button size="compact">Action</Button>} />}
    >
      <SkipLink />
      <PageTransition>
        <PageContainer>AppShell main content</PageContainer>
      </PageTransition>
    </AppShell>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "AppShell, AppHeader, SkipLink, and PageTransition establish landmarks and preserve a keyboard route to main content.",
      },
    },
  },
};

export const HeaderAliases: Story = {
  render: () => (
    <div className="grid gap-5">
      <TopNavbar title="TopNavbar" actions={<Button>Action</Button>} />
      <Navbar title="Navbar alias" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "TopNavbar and Navbar are aliases of AppHeader and share responsive title, search, leading, and action slots.",
      },
    },
  },
};

export const WorkspaceApplicationShell: Story = {
  render: () => (
    <WorkspaceShell>
      <PageContainer>WorkspaceShell composes the production sidebar and header.</PageContainer>
    </WorkspaceShell>
  ),
  parameters: {
    nextjs: { appDirectory: true, navigation: { pathname: "/dashboard" } },
    docs: {
      description: {
        story:
          "WorkspaceShell is shown with Next App Router mocks and the global Sidebar and Theme providers.",
      },
    },
  },
};
