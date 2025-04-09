import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState(null);
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState(null);
  const[firstName, setFirstName] = useState(null);
  const[lastName, setLastName] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
      const userData = localStorage.getItem("userData");
      const storedToken = localStorage.getItem("token");
      const userName = localStorage.getItem("username");
      const firstName = localStorage.getItem("firstName")
      const lastName = localStorage.getItem("lastName")

      setUsername(userName);
      setAuth(userData);
      setToken(storedToken);
      setFirstName(firstName)
      setLastName(lastName)
      setLoading(false);
  }, []);

  const login = (userData, authToken, userName) => {
    localStorage.setItem("userData", JSON.stringify(userData));
    localStorage.setItem("username", userName);
    localStorage.setItem("token", authToken);
    localStorage.setItem('firstName', userData.firstName);
    localStorage.setItem('lastName', userData.lastName);

    setAuth(userData);
    setToken(authToken);
    setUsername(userName);
    setFirstName(firstName)
    setLastName(lastName)
  };

  const logout = () => {
    localStorage.removeItem("userData");
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem('firstName')
    localStorage.removeItem('lastName')

    setAuth(null);
    setToken(null);
    setUsername(null);
    setFirstName(null);
    setLastName(null)
  };

  return (
    <AuthContext.Provider value={{ auth, token, username, login, logout, loading, isAuthenticated: !!auth && !!token }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};