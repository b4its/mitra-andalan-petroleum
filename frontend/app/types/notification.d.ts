// export interface Notifications {
//   id: string;
//   unread: boolean;
//   sender: Sender;
//   body: string;
//   date: Date | string;
// }

// export interface Sender {
//   name: string;
//   avatar: Avatar;
// }

// export interface Avatar {
//   src: string;
//   alt: string;
// }

export interface Notifications {
  id: string;
  title: string;
  message: string;
  type: string;
  sender_id: string;
  created_at: Date;
}
