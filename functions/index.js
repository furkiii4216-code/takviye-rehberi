const { onDocumentCreated } = require("firebase-functions/v2/firestore");
const admin = require("firebase-admin");

admin.initializeApp();

// announcements koleksiyonuna yeni duyuru eklenince tum kayitli cihazlara push gonderir.
exports.sendAnnouncementPush = onDocumentCreated("announcements/{id}", async (event) => {
  const data = event.data && event.data.data();
  if (!data) return;

  const db = admin.firestore();
  const snap = await db.collection("fcm_tokens").get();

  // token -> belge eslemesi (gecersiz tokenlari temizlemek icin)
  const owner = new Map();
  snap.forEach((d) => {
    (d.data().tokens || []).forEach((t) => owner.set(t, d.ref));
  });
  const tokens = Array.from(owner.keys());
  if (tokens.length === 0) return;

  for (let i = 0; i < tokens.length; i += 500) {
    const chunk = tokens.slice(i, i + 500);
    const res = await admin.messaging().sendEachForMulticast({
      tokens: chunk,
      notification: {
        title: String(data.title || "Duyuru").slice(0, 100),
        body: String(data.message || "").slice(0, 300),
      },
      android: { priority: "high" },
    });

    const cleanups = [];
    res.responses.forEach((r, idx) => {
      const code = r.error && r.error.code;
      if (
        code === "messaging/registration-token-not-registered" ||
        code === "messaging/invalid-registration-token"
      ) {
        const t = chunk[idx];
        cleanups.push(owner.get(t).update({ tokens: admin.firestore.FieldValue.arrayRemove(t) }));
      }
    });
    await Promise.all(cleanups);
  }
});
