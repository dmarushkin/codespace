import React from 'react';
import { Link } from 'react-router-dom';
import { Menu } from 'antd';

const Navbar = () => (
  <Menu mode="horizontal">
    <Menu.Item>
      <Link to="/">Home</Link>
    </Menu.Item>
    <Menu.Item>
      <Link to="/login">Login</Link>
    </Menu.Item>
    <Menu.Item>
      <Link to="/admin">Admin</Link>
    </Menu.Item>
  </Menu>
);

export default Navbar;
