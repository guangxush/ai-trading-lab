import React from 'react'
import { Layout, Menu } from 'antd'
import {
  StockOutlined,
  LineChartOutlined,
  AppstoreOutlined,
  WalletOutlined
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'

const { Header, Sider, Content } = Layout

interface MainLayoutProps {
  children: React.ReactNode
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <StockOutlined />,
      label: '大盘监控',
    },
    {
      key: '/backtest',
      icon: <LineChartOutlined />,
      label: '策略回测',
    },
    {
      key: '/skills',
      icon: <AppstoreOutlined />,
      label: 'SKILL市场',
    },
    {
      key: '/portfolio',
      icon: <WalletOutlined />,
      label: '持仓管理',
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} theme="dark">
        <div
          style={{
            height: 64,
            color: '#fff',
            textAlign: 'center',
            fontSize: 18,
            fontWeight: 'bold',
            lineHeight: '64px',
            borderBottom: '1px solid rgba(255,255,255,0.1)',
          }}
        >
          📈 AI Trading Lab
        </div>
        <Menu
          theme="dark"
          selectedKeys={[location.pathname]}
          mode="inline"
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 500 }}>
            AI量化交易平台
          </span>
        </Header>
        <Content
          style={{
            margin: 24,
            background: '#fff',
            padding: 24,
            borderRadius: 8,
            minHeight: 280,
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}