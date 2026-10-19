importScripts('https://www.gstatic.com/firebasejs/9.22.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.22.1/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyBDglc3Z7VuGxGpxt7u43kk17aFxszAIeA",
  authDomain: "trson1.firebaseapp.com",
  projectId: "trson1",
  storageBucket: "trson1.firebasestorage.app",
  messagingSenderId: "311650569694",
  appId: "1:311650569694:web:cdd29f6228930415e5614f"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  const notificationTitle = payload.notification.title || "Yeni Bildirim";
  const notificationOptions = {
    body: payload.notification.body || "Yeni bir duyurunuz var.",
    icon: "/favicon.ico"
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
