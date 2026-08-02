"use client";

import * as ToastPrimitive from "@radix-ui/react-toast";
import { X } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui";

export type ToastRequest = { title: string; description?: string; duration?: number };
export type ToastApi = { toast: (request: ToastRequest) => void };
export type AppToastProviderProps = { children: React.ReactNode };

const ToastContext = React.createContext<ToastApi | null>(null);

export function AppToastProvider({ children }: AppToastProviderProps): React.JSX.Element {
  const [request, setRequest] = React.useState<ToastRequest | null>(null);
  return (
    <ToastContext.Provider value={{ toast: setRequest }}>
      <ToastPrimitive.Provider>
        {children}
        {request && (
          <ToastPrimitive.Root
            open
            onOpenChange={(open) => {
              if (!open) setRequest(null);
            }}
            {...(request.duration !== undefined ? { duration: request.duration } : {})}
            className="bg-popover text-popover-foreground shadow-popover relative rounded-lg border p-4 pr-12"
          >
            <ToastPrimitive.Title className="font-semibold">{request.title}</ToastPrimitive.Title>
            {request.description && (
              <ToastPrimitive.Description className="text-muted-foreground mt-1 text-sm">
                {request.description}
              </ToastPrimitive.Description>
            )}
            <ToastPrimitive.Close asChild>
              <Button
                variant="icon"
                className="absolute top-2 right-2"
                aria-label="Dismiss notification"
              >
                <X aria-hidden="true" />
              </Button>
            </ToastPrimitive.Close>
          </ToastPrimitive.Root>
        )}
        <ToastPrimitive.Viewport className="fixed right-0 bottom-0 z-100 flex w-full max-w-sm flex-col gap-2 p-4" />
      </ToastPrimitive.Provider>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastApi {
  const value = React.useContext(ToastContext);
  if (!value) throw new Error("useToast must be used within AppToastProvider.");
  return value;
}
