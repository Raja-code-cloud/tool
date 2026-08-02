export { formatBytes } from "@/lib/utils/formatting";

export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export async function readVideoDuration(file: File): Promise<string> {
  return new Promise((resolve) => {
    const video = document.createElement("video");
    video.preload = "metadata";
    video.onloadedmetadata = () => {
      URL.revokeObjectURL(video.src);
      resolve(formatDuration(video.duration));
    };
    video.onerror = () => {
      URL.revokeObjectURL(video.src);
      resolve("—");
    };
    video.src = URL.createObjectURL(file);
  });
}

export async function readTextFile(file: File): Promise<string> {
  return file.text();
}
