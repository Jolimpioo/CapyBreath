import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthContext } from '../features/auth/AuthProvider';

type NavItem = {
  to: string;
  label: string;
};

const publicItems: NavItem[] = [
  { to: '/', label: 'Início' },
  { to: '/community', label: 'Comunidade' },
];

const privateItems: NavItem[] = [
  { to: '/', label: 'Praticar' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/session', label: 'Sessões' },
  { to: '/achievements', label: 'Conquistas' },
  { to: '/profile', label: 'Perfil' },
  { to: '/community', label: 'Comunidade' },
];

const baseNavLinkClass =
  'inline-flex min-h-[44px] items-center rounded px-3 py-2 text-white/95 hover:bg-white/10';

const Navbar = () => {
  const { user, logout } = useAuthContext();
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const closeMenu = () => setMobileOpen(false);

  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeMenu();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, []);

  const isActivePath = (path: string) =>
    path === '/'
      ? location.pathname === path
      : location.pathname === path || location.pathname.startsWith(`${path}/`);

  const resolveNavLinkClass = (path: string) =>
    `${baseNavLinkClass} ${isActivePath(path) ? 'bg-white/20 font-semibold' : ''}`.trim();

  const renderDesktopLinks = (items: NavItem[]) => (
    <div
      className="hidden items-center gap-2 md:flex"
      aria-label="Navegação principal desktop"
    >
      {items.map(item => (
        <Link
          key={item.to}
          to={item.to}
          className={resolveNavLinkClass(item.to)}
          aria-current={isActivePath(item.to) ? 'page' : undefined}
        >
          {item.label}
        </Link>
      ))}
    </div>
  );

  const renderMobileLinks = (items: NavItem[]) => (
    <div
      id="primary-navigation"
      className="space-y-2 border-t border-white/20 px-4 pb-4 pt-3 md:hidden"
      aria-label="Navegação principal mobile"
    >
      {items.map(item => (
        <Link
          key={item.to}
          to={item.to}
          className={`${resolveNavLinkClass(item.to)} w-full`}
          onClick={closeMenu}
          aria-current={isActivePath(item.to) ? 'page' : undefined}
        >
          {item.label}
        </Link>
      ))}
    </div>
  );

  return (
    <nav
      className="w-full bg-capy-primary text-white shadow"
      aria-label="Barra principal"
    >
      <div className="mx-auto flex min-h-[64px] w-full max-w-6xl items-center justify-between px-4 md:px-6">
        <Link
          to="/"
          className="text-xl font-bold text-white hover:text-white"
          onClick={closeMenu}
        >
          CapyBreath
        </Link>

        <button
          type="button"
          className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded border border-white/40 px-3 md:hidden"
          onClick={() => setMobileOpen(prev => !prev)}
          aria-label={mobileOpen ? 'Fechar menu' : 'Abrir menu'}
          aria-expanded={mobileOpen}
          aria-controls="primary-navigation"
        >
          {mobileOpen ? '✕' : '☰'}
        </button>

        {!user ? (
          <>
            {renderDesktopLinks(publicItems)}
            <div className="hidden items-center gap-2 md:flex">
              <Link to="/login" className="ui-btn ui-btn--secondary">
                Login
              </Link>
              <Link
                to="/register"
                className="ui-btn ui-btn--ghost border-white text-white"
              >
                Registrar
              </Link>
            </div>
          </>
        ) : (
          <>
            {renderDesktopLinks(privateItems)}
            <div className="hidden items-center gap-2 md:flex">
              <span className="px-2 text-sm font-semibold">
                {user.full_name || user.username}
              </span>
              <button
                onClick={() => {
                  void logout();
                }}
                className="ui-btn ui-btn--secondary"
              >
                Sair
              </button>
            </div>
          </>
        )}
      </div>

      {mobileOpen && (
        <>
          {!user ? (
            <div>
              {renderMobileLinks(publicItems)}
              <div className="space-y-2 px-4 pb-4 md:hidden">
                <Link
                  to="/login"
                  className="ui-btn ui-btn--secondary w-full text-center"
                  onClick={closeMenu}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="ui-btn ui-btn--ghost w-full border-white text-center text-white"
                  onClick={closeMenu}
                >
                  Registrar
                </Link>
              </div>
            </div>
          ) : (
            <div>
              {renderMobileLinks(privateItems)}
              <div className="px-4 pb-4 md:hidden">
                <div className="px-2 pb-2 pt-1 text-sm font-semibold">
                  {user.full_name || user.username}
                </div>
                <button
                  onClick={() => {
                    closeMenu();
                    void logout();
                  }}
                  className="ui-btn ui-btn--secondary w-full"
                >
                  Sair
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </nav>
  );
};

export default Navbar;
