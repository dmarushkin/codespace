import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Select, List, Modal } from 'antd';
import api from '../api';

const { Option } = Select;

const AdminPage = () => {
  const [users, setUsers] = useState([]);
  const [tokens, setTokens] = useState([]);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [type, setType] = useState('user');
  const [tokenName, setTokenName] = useState('');
  const [token, setToken] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const fetchUsers = async () => {
    try {
      const response = await api.get('/users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users', error);
    }
  };

  const fetchTokens = async () => {
    try {
      const response = await api.get('/tokens/');
      setTokens(response.data);
    } catch (error) {
      console.error('Failed to fetch tokens', error);
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchTokens();
  }, []);

  const addUser = async () => {
    try {
      await api.post('/users/', { email, password, type });
      fetchUsers();
    } catch (error) {
      console.error('Failed to add user', error);
    }
  };

  const deleteUser = async (userId) => {
    try {
      await api.delete(`/users/${userId}`);
      fetchUsers();
    } catch (error) {
      console.error('Failed to delete user', error);
    }
  };

  const changeUserType = async (userId, newType) => {
    try {
      await api.put(`/users/${userId}/type`, { new_type: newType });
      fetchUsers();
    } catch (error) {
      console.error('Failed to change user type', error);
    }
  };

  const addToken = async () => {
    try {
      const response = await api.post('/tokens/', { token_name: tokenName });
      setToken(response.data.access_token);
      fetchTokens();
    } catch (error) {
      console.error('Failed to add token', error);
    }
  };

  const deleteToken = async (tokenId) => {
    try {
      await api.delete(`/tokens/${tokenId}`);
      fetchTokens();
    } catch (error) {
      console.error('Failed to delete token', error);
    }
  };

  const changePassword = async () => {
    try {
      await api.put(`/users/${selectedUser.id}/password`, { old_password: oldPassword, new_password: newPassword });
      alert('Password changed successfully');
    } catch (error) {
      console.error('Failed to change password', error);
      alert('Failed to change password');
    }
  };

  return (
    <div>
      <h1>Admin Page</h1>

      <Button onClick={() => {
              Modal.confirm({
                title: 'Add User',
                content: (
                  <Form onFinish={addUser}>
                  <Form.Item>
                    <Input
                      placeholder="Email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </Form.Item>
                  <Form.Item>
                    <Input.Password
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </Form.Item>
                  <Form.Item>
                    <Select value={type} onChange={(value) => setType(value)}>
                      <Option value="user">User</Option>
                      <Option value="admin">Admin</Option>
                    </Select>
                  </Form.Item>
                  <Form.Item>
                    <Button type="primary" htmlType="submit">
                      Add User
                    </Button>
                  </Form.Item>
                </Form>
                ),
                onOk: addUser,
              });
            }}>Add user</Button>

     
      <List
        header={<div>Users</div>}
        bordered
        dataSource={users}
        renderItem={(item) => (
          <List.Item actions={[
            <Button onClick={() => deleteUser(item.id)}>Delete</Button>,
            <Button onClick={() => {
              setSelectedUser(item);
              Modal.confirm({
                title: 'Change Password',
                content: (
                  <Form onFinish={changePassword}>
                    <Form.Item>
                      <Input.Password
                        placeholder="Old Password"
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                      />
                    </Form.Item>
                    <Form.Item>
                      <Input.Password
                        placeholder="New Password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                      />
                    </Form.Item>
                  </Form>
                ),
                onOk: changePassword,
              });
            }}>Change Password</Button>
          ]}>
            {item.email}
          </List.Item>
        )}
      />
      <Form onFinish={addToken}>
        <Form.Item>
          <Input
            placeholder="Token Name"
            value={tokenName}
            onChange={(e) => setTokenName(e.target.value)}
          />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Add Token
          </Button>
        </Form.Item>
      </Form>
      <List
        header={<div>Tokens</div>}
        bordered
        dataSource={tokens}
        renderItem={(item) => (
          <List.Item actions={[
            <Button onClick={() => deleteToken(item.id)}>Delete</Button>
          ]}>
            {item.token_name} - {item.token}
          </List.Item>
        )}
      />
    </div>
  );
};

export default AdminPage;