# KZZ Football Live — ဘောလုံး Live Scores Website

ဘောလုံး live scores, လာမယ့်ပွဲစဉ်၊ ပြီးခဲ့တဲ့ရလဒ်၊ အဆင့်ဇယား နဲ့ ပွဲကြိုခန့်မှန်းချက်တွေ ပြတဲ့ website။
ဘာသာစကား: မြန်မာ။ ဖုန်း + ကွန်ပျူတာ နှစ်မျိုးလုံး အဆင်ပြေအောင် လုပ်ထားတယ်။

## ပါဝင်တာတွေ
- 🔴 တိုက်ရိုက် — ကစားနေတဲ့ပွဲတွေ (၆၀ စက္ကန့်တစ်ခါ auto-refresh)
- 📅 ပွဲစဉ် — နောက် ၇ ရက်အတွင်း လာမယ့်ပွဲတွေ
- ✅ ရလဒ် — ပြီးခဲ့တဲ့ ရလဒ်တွေ
- 📊 အဆင့် — အဆင့်ဇယား
- 🔮 ခန့်မှန်းချက် — `predictions.json` က ခန့်မှန်းချက်တွေ

လိဂ် ၇ ခု: Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Champions League, Europa League

## ဒေတာ အရင်းအမြစ်
- ရမှတ်/ပွဲစဉ်/အဆင့်: ESPN public API (အခမဲ့၊ API key မလို) — browser က တိုက်ရိုက်ဆွဲတာ
- ⚠️ ဗီဒီယို တိုက်ရိုက်ထုတ်လွှင့်မှု (stream) **မပါဘူး** — မူပိုင်ခွင့်ရှိတဲ့ ရုပ်သံမဟုတ်ဘဲ ပြန်ထုတ်လွှင့်လို့ မရလို့

## အင်တာနက်ပေါ် တင်နည်း (အခမဲ့၊ ၂ မိနစ်)
အလွယ်ဆုံးနည်း — Netlify Drop:
1. https://app.netlify.com/drop ကို ဖွင့် (အကောင့်ဖွင့်ဖို့ လိုတယ်၊ အခမဲ့)
2. ဒီ folder (`kzz-football-live`) တစ်ခုလုံးကို drag-and-drop လုပ်
3. ပြီးရင် public link တစ်ခု ရမယ် (ဥပမာ `kzz-football-live.netlify.app`)

အခြားနည်းတွေ: Vercel, Cloudflare Pages, GitHub Pages — folder upload / git push နဲ့ ရတယ်။

## ခန့်မှန်းချက် အပ်ဒိတ်လုပ်နည်း
`predictions.json` ကို ဒီပုံစံအတိုင်း ပြင်ပြီး site ကို ပြန်တင် (re-deploy):

```json
{
  "updated": "2026-10-11",
  "source": "KZZ Football Analysis",
  "predictions": [
    {
      "league": "Premier League",
      "home": "Arsenal",
      "away": "Chelsea",
      "date": "2026-10-11T20:00:00+06:30",
      "pick": "Arsenal နိုင်မယ်",
      "confidence": "high",
      "reason_mm": "အိမ်ကွင်းခြေစွမ်းကောင်း၊ နောက်ဆုံး ၅ ပွဲမှာ ၄ ပွဲနိုင်…"
    }
  ]
}
```
- `confidence`: `high` / `medium` / `low`
- Muse ကို ခိုင်းရင် KZZ prediction cron ကနေ auto-update လုပ်ပေးလို့ရတယ် — ပြောရုံပဲ။

## ဖိုင်တွေ
- `index.html` — စာမျက်နှာ
- `styles.css` — ဒီဇိုင်း
- `app.js` — လုပ်ဆောင်ချက် (ESPN API ခေါ်တာ)
- `predictions.json` — ခန့်မှန်းချက်များ
