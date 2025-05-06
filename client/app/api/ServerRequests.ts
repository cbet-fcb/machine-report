/* eslint-disable @typescript-eslint/no-explicit-any */
import Server from "./Server";

class ServerRequests extends Server {
  constructor() {
    super();
  }

  streamProcessImage(file: File, onMessage: (data: any) => void) {
    const formData = new FormData();
    formData.append("file", file);

    // First, upload the file using POST
    fetch(`${this.apiUrl}/upload`, {
      method: "POST",
      body: formData,
    })
      .then(() => {
        // Then, listen for progress using SSE
        const eventSource = new EventSource(
          `${this.apiUrl}/streamProcessImage`
        );

        eventSource.onmessage = (event) => {
          const parsed = JSON.parse(event.data);
          onMessage(parsed);

          // Optionally close when complete
          if (parsed.progress === 100) {
            eventSource.close();
          }
        };

        eventSource.onerror = (err) => {
          console.error("SSE error:", err);
          eventSource.close();
        };
      })
      .catch((err) => {
        console.error("Upload error:", err);
      });
  }
}

export default ServerRequests;
