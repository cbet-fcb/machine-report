/* eslint-disable @typescript-eslint/no-explicit-any */
import { th } from "framer-motion/client";
import Server from "./Server";

class ServerRequests extends Server {
  constructor() {
    super();
  }

  streamProcessImage(file: File, onMessage: (data: any) => void) {
    const formData = new FormData();
    formData.append("file", file);

    fetch(`${this.apiUrl}/streamProcessImage`, {
      method: "POST",
      body: formData,
    })
      .then((res) => {
        const reader = res.body?.getReader();
        const decoder = new TextDecoder("utf-8");

        let buffer = "";

        function readStream() {
          if (!reader) return;

          reader.read().then(({ done, value }) => {
            if (done) return;

            buffer += decoder.decode(value, { stream: true });

            const parts = buffer.split("\n\n");
            buffer = parts.pop() || "";

            for (const part of parts) {
              if (part.startsWith("data: ")) {
                const jsonStr = part.slice(6).trim();
                try {
                  const data = JSON.parse(jsonStr);
                  onMessage(data);
                } catch (e) {
                  console.error("Invalid JSON:", jsonStr);
                }
              }
            }

            readStream();
          });
        }

        readStream();

        return res.text();
      })
      .catch((err) => {
        console.error("Upload/stream error:", err);
      });
  }
}

export default ServerRequests;
