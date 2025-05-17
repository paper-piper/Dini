const handleLogin = async (username: string, password: string) => {
  try {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    
    // Store both username and session_id
    setUser({
      username,
      session_id: data.session_id
    });

    // Redirect to dashboard
    router.push('/');
  } catch (error) {
    console.error('Login error:', error);
    // Show error message to user
  }
}; 