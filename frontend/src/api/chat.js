export async function postChat(payload) {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
  const response = await fetch(`${baseUrl}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(errorText || '聊天接口调用失败')
  }

  return response.json()
}
