import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../features/auth/AuthProvider';

const Navbar = () => {
  const { user, logout } = useAuthContext();
  const navigate = useNavigate();

  if (!user) {
    return (
      <nav className="w-full bg-capy-primary text-white py-3 px-6 flex items-center justify-between shadow">
        <div className="flex items-center gap-6">
          <Link to="/" className="font-bold text-xl hover:underline">
            CapyBreath
          </Link>
        </div>
        <div className="flex items-center gap-4">
          <Link
            to="/login"
            className="bg-white text-capy-primary font-bold px-3 py-1 rounded hover:bg-gray-100 transition"
          >
            Login
          </Link>
          <Link
            to="/register"
            className="bg-white text-capy-primary font-bold px-3 py-1 rounded hover:bg-gray-100 transition"
          >
            Registrar
          </Link>
        </div>
      </nav>
    );
  }

  return (
    <nav className="w-full bg-capy-primary text-white py-3 px-6 flex items-center justify-between shadow">
      <div className="flex items-center gap-6">
        <Link to="/" className="font-bold text-xl hover:underline">
          CapyBreath
        </Link>
        <Link to="/session" className="hover:underline">
          Sessões
        </Link>
        <Link to="/achievements" className="hover:underline">
          Conquistas
        </Link>
        <Link to="/profile" className="hover:underline">
          Perfil
        </Link>
      </div>
      <div className="flex items-center gap-4">
        <span className="font-semibold">{user.name}</span>
        <button
          onClick={() => {
            logout();
            navigate('/login');
          }}
          className="bg-white text-capy-primary font-bold px-3 py-1 rounded hover:bg-gray-100 transition"
        >
          Sair
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
