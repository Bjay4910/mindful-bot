// Frontend configuration — do NOT put secret keys here
const CONFIG = {
    SUPABASE_URL: 'https://qznbwrfvlsijpgnxugbp.supabase.co',
    SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_agKK0Mg_3QBsMTLwO85UrQ_jaC51hCh',
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:5001/api'
        : 'https://mindful-bot.onrender.com/api',
};
