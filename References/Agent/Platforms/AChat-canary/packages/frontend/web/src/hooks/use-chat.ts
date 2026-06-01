import { useHC, useHCMutation } from "@/hooks/use-hono-swr";
import apiClient from "@/lib/api-client";

// interface UseConversationOptions {
//   id?: string;
//   onMessage?: (message: string) => void;
// }

export type UseConversation = {
  // messages: Message[];
  sendMessage: (userInput: string) => Promise<void>;
  editMessage: (messageId: string, userInput: string) => Promise<void>;
  deleteMessage: (messageId: string) => Promise<void>;
};

export default function useConversation(id?: string) {
  const conversationSWR = useHC(
    apiClient.user.chat.conversation[":id"].messages.$get,
    id
      ? {
          param: {
            id,
          },
        }
      : null
  );

  const newMessage = useHCMutation(
    apiClient.user.chat.conversation[":id?"].$post
  );

  const sendMessage = async (userInput: string) => {
    await newMessage.trigger({
      param: {
        id,
      },
      json: {
        prompt: userInput,
      },
    });
  };

  return {};
}
