const BASE_URL = 'https://velora-backend-production.up.railway.app';

export async function loginGoogle(data) {
  const res = await fetch(`${BASE_URL}/auth/google`, { // Akan menjadi /api/auth/google
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function saveProfile(data) {
  const res = await fetch(`${BASE_URL}/user-profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function getProfile(userId) {
  const res = await fetch(`${BASE_URL}/user-profile/${userId}`);
  return res.json();
}

export async function getMenuRecommendation(userId) {
  const res = await fetch(`${BASE_URL}/recommendation/${userId}`);
  return res.json();
}
