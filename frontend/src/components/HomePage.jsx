import React from 'react';
import './HomePage.css';
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

const HomePage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAuthData = async () => {
      try {
        const res = await axios.get("http://localhost:8000/api/microsoft-login/", {
          withCredentials: true,
        });

        const { access_token, refresh_token, user } = res.data;

        // Save to localStorage (optional)
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
        localStorage.setItem("userData", JSON.stringify(user));

        // Set user in context
        login({
          userId: user.id,
          name: user.name,
          email: user.email,
          role: user.role,
          status: user.status,
        });

        // optionally: navigate('/dashboard') if this isn’t Home
      } catch (err) {
        console.error("Failed to fetch auth data:", err);
        navigate("/login");
      }
    };

    fetchAuthData();
  }, [login, navigate]);

  return (
    <div className="home-container">
      <div className="box-container">
        <div className="box">
          <h2>Welcome to Uranium City</h2>
          <p>Under Maintenance</p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
