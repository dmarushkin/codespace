import React, { useState } from 'react';
import { Form, Input, Button } from 'antd';
import api from '../api';

const ProfilePage = () => {
  const [loading, setLoading] = useState(false);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const onFinish = async () => {
    setLoading(true);
    try {
      await api.put('/users/me/password', { old_password: oldPassword, new_password: newPassword });
      alert('Password changed successfully');
    } catch (error) {
      console.error('Failed to change password', error);
      alert('Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form onFinish={onFinish}>
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
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading}>
          Change Password
        </Button>
      </Form.Item>
    </Form>
  );
};

export default ProfilePage;