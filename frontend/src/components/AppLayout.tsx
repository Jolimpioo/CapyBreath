import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

const AppLayout = () => (
  <div className="flex min-h-screen flex-col bg-capy-light">
    <Navbar />
    <main className="flex-1">
      <Outlet />
    </main>
  </div>
);

export default AppLayout;
