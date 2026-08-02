import type { Meta, StoryObj } from "@storybook/react";
import { Home, Settings } from "lucide-react";
import * as React from "react";

import {
  Breadcrumbs,
  NavItem,
  NotificationButton,
  Pagination,
  SearchBar,
  Sidebar,
  SidebarMenu,
  SidebarTrigger,
  Tabs,
  UserMenu,
} from "../components/navigation";
import { DropdownMenuItem } from "../components/ui";

const items = [
  { label: "Dashboard", href: "#dashboard", icon: <Home /> },
  { label: "Settings", href: "#settings", icon: <Settings />, badge: "2" },
];

const meta = {
  title: "Navigation/Navigation",
  component: Breadcrumbs,
  args: { items: [{ label: "Home", href: "#" }, { label: "Current page" }] },
  parameters: {
    docs: {
      description: {
        component:
          "Navigation patterns use landmark labels, current-page semantics, keyboard operation, and responsive layouts. Sidebar stories run inside the global SidebarProvider.",
      },
    },
  },
} satisfies Meta<typeof Breadcrumbs>;

export default meta;
type Story = StoryObj<typeof meta>;

export const BreadcrumbTrail: Story = {
  args: {
    items: [
      { label: "Home", href: "#" },
      { label: "Campaigns", href: "#campaigns" },
      { label: "Launch" },
    ],
  },
  parameters: {
    docs: {
      description: {
        story:
          "Breadcrumbs collapses intermediate items on narrow screens while retaining the current page.",
      },
    },
  },
};

export const TabNavigation: Story = {
  render: function ControlledTabs() {
    const [value, setValue] = React.useState("overview");
    return (
      <>
        <Tabs
          label="Campaign sections"
          value={value}
          onValueChange={setValue}
          items={[
            { id: "overview", label: "Overview" },
            { id: "content", label: "Content" },
            { id: "disabled", label: "Disabled", disabled: true },
          ]}
        />
        <div role="tabpanel" id={`panel-${value}`} aria-labelledby={`tab-${value}`} className="p-4">
          Selected: {value}
        </div>
      </>
    );
  },
  parameters: {
    docs: {
      description: {
        story:
          "Tabs supports click and left/right arrow navigation, disabled tabs, and controlled selection.",
      },
    },
  },
};

export const PaginationStory: Story = {
  render: function ControlledPagination() {
    const [page, setPage] = React.useState(2);
    return (
      <Pagination page={page} pageCount={8} pageSize={20} total={143} onPageChange={setPage} />
    );
  },
  parameters: {
    docs: {
      description: {
        story:
          "Pagination provides previous/next controls, bounded disabled states, and a readable item range.",
      },
    },
  },
};

export const SidebarFamily: Story = {
  render: () => (
    <div className="desktop:grid-cols-[15rem_1fr] grid gap-6">
      <Sidebar
        className="relative inset-auto h-80 translate-x-0"
        items={items}
        currentHref="#dashboard"
        header={<strong>Workspace</strong>}
        footer={<span>Footer</span>}
      />
      <div className="grid content-start gap-4">
        <SidebarTrigger className="flex" />
        <SidebarMenu items={items} currentHref="#settings" />
        <NavItem href="#custom" icon={<Home />} isActive>
          Standalone item
        </NavItem>
      </div>
    </div>
  ),
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        story:
          "Sidebar, SidebarMenu, SidebarTrigger, and NavItem. The trigger controls the provider-backed mobile drawer; current location is announced with aria-current.",
      },
    },
  },
};

export const HeaderActions: Story = {
  render: () => (
    <div className="flex items-center gap-3">
      <SearchBar placeholder="Search workspace" />
      <NotificationButton count={3} className="relative" />
      <UserMenu name="Ada Lovelace" email="ada@example.com">
        <DropdownMenuItem>Profile</DropdownMenuItem>
        <DropdownMenuItem>Sign out</DropdownMenuItem>
      </UserMenu>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "SearchBar, NotificationButton, and UserMenu remain keyboard accessible; unread count is included in the notification label.",
      },
    },
  },
};
