// pages/api/events.ts
import { NextApiRequest, NextApiResponse } from 'next';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
  });

  const sendEvent = (data: string) => {
    res.write(`data: ${data}\n\n`);
  };

  // Send a message every 5 seconds
  const interval = setInterval(() => {
    sendEvent(`Server time: ${new Date().toLocaleTimeString()}`);
  }, 5000);

  // Cleanup on client disconnect
  req.on('close', () => {
    clearInterval(interval);
    res.end();
  });
}
