import React, { useState, useEffect } from 'react'
import {
  Card, Row, Col, Table, Button, Modal, Form, InputNumber,
  Select, message, Statistic, Tag, Tabs, List, Typography, Spin
} from 'antd'
import {
  WalletOutlined, RiseOutlined, FallOutlined,
  ShoppingCartOutlined, HistoryOutlined, AlertOutlined
} from '@ant-design/icons'
import {
  getAccount, getPositions, createOrder, getOrders,
  getTradeHistory, assessRisk, analyzePortfolio
} from '../api/trading'

const { Title, Text } = Typography
const { TabPane } = Tabs

interface Position {
  symbol: string
  market: string
  shares: number
  avg_cost: number
  current_price: number
  market_value: number
  profit_loss: number
  profit_loss_percent: number
}

export const Portfolio: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [account, setAccount] = useState<any>({})
  const [positions, setPositions] = useState<Position[]>([])
  const [orders, setOrders] = useState<any[]>([])
  const [tradeHistory, setTradeHistory] = useState<any[]>([])
  const [riskAssessment, setRiskAssessment] = useState<any>({})
  const [portfolioAnalysis, setPortfolioAnalysis] = useState<any>({})
  const [tradeModalVisible, setTradeModalVisible] = useState(false)
  const [tradeForm] = Form.useForm()

  const fetchData = async () => {
    setLoading(true)
    try {
      const [accountData, positionsData, ordersData, historyData, riskData, portfolioData] = await Promise.all([
        getAccount().catch(() => ({})),
        getPositions().catch(() => ({ positions: [] })),
        getOrders().catch(() => []),
        getTradeHistory(20).catch(() => []),
        assessRisk().catch(() => ({})),
        analyzePortfolio().catch(() => ({})),
      ])

      setAccount(accountData)
      setPositions(positionsData.positions || [])
      setOrders(ordersData)
      setTradeHistory(historyData)
      setRiskAssessment(riskData)
      setPortfolioAnalysis(portfolioData)
    } catch (error) {
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleTrade = async (values: any) => {
    try {
      await createOrder({
        symbol: values.symbol,
        side: values.side,
        shares: values.shares,
        order_type: values.order_type || 'market',
        price: values.price,
        market: 'cn'
      })
      message.success('订单创建成功')
      setTradeModalVisible(false)
      tradeForm.resetFields()
      fetchData()
    } catch (error) {
      message.error('订单创建失败')
    }
  }

  const getRiskLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      low: 'green',
      medium: 'orange',
      high: 'red',
      critical: 'magenta',
    }
    return colors[level] || 'default'
  }

  const positionColumns = [
    {
      title: '股票代码',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: '持仓数量',
      dataIndex: 'shares',
      key: 'shares',
    },
    {
      title: '成本价',
      dataIndex: 'avg_cost',
      key: 'avg_cost',
      render: (v: number) => `¥${v.toFixed(2)}`,
    },
    {
      title: '现价',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (v: number) => `¥${v.toFixed(2)}`,
    },
    {
      title: '市值',
      dataIndex: 'market_value',
      key: 'market_value',
      render: (v: number) => `¥${v.toFixed(2)}`,
    },
    {
      title: '盈亏',
      dataIndex: 'profit_loss',
      key: 'profit_loss',
      render: (v: number, record: Position) => (
        <span style={{ color: v >= 0 ? '#f5222d' : '#52c41a' }}>
          {v >= 0 ? '+' : ''}{v.toFixed(2)} ({v >= 0 ? '+' : ''}{record.profit_loss_percent.toFixed(2)}%)
        </span>
      ),
    },
  ]

  const orderColumns = [
    {
      title: '订单ID',
      dataIndex: 'order_id',
      key: 'order_id',
      width: 100,
      ellipsis: true,
    },
    {
      title: '股票',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      render: (v: string) => (
        <Tag color={v === 'buy' ? 'green' : 'red'}>
          {v === 'buy' ? '买入' : '卖出'}
        </Tag>
      ),
    },
    {
      title: '数量',
      dataIndex: 'shares',
      key: 'shares',
    },
    {
      title: '成交价',
      dataIndex: 'filled_price',
      key: 'filled_price',
      render: (v: number) => v ? `¥${v.toFixed(2)}` : '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (v: string) => {
        const colors: Record<string, string> = {
          pending: 'blue',
          submitted: 'cyan',
          filled: 'green',
          cancelled: 'default',
          rejected: 'red',
        }
        return <Tag color={colors[v] || 'default'}>{v}</Tag>
      },
    },
  ]

  return (
    <div>
      <Title level={2}>
        <WalletOutlined /> 持仓管理
      </Title>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <Spin size="large" />
        </div>
      ) : (
        <>
          {/* 账户概览 */}
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={6}>
              <Card>
                <Statistic
                  title="总资产"
                  value={account.total_assets || 0}
                  precision={2}
                  prefix="¥"
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="可用资金"
                  value={account.available_balance || 0}
                  precision={2}
                  prefix="¥"
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="持仓市值"
                  value={portfolioAnalysis.total_value || 0}
                  precision={2}
                  prefix="¥"
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="总盈亏"
                  value={portfolioAnalysis.total_profit || 0}
                  precision={2}
                  prefix="¥"
                  valueStyle={{ color: (portfolioAnalysis.total_profit || 0) >= 0 ? '#f5222d' : '#52c41a' }}
                />
              </Card>
            </Col>
          </Row>

          {/* 风险提示 */}
          {riskAssessment.risk_level && (
            <Card style={{ marginBottom: 24 }}>
              <Row gutter={16} align="middle">
                <Col>
                  <AlertOutlined style={{ fontSize: 24 }} />
                </Col>
                <Col flex="auto">
                  <Text>
                    风险等级:
                    <Tag color={getRiskLevelColor(riskAssessment.risk_level)} style={{ marginLeft: 8 }}>
                      {riskAssessment.risk_level.toUpperCase()}
                    </Tag>
                  </Text>
                  {riskAssessment.alerts?.length > 0 && (
                    <Text type="secondary" style={{ marginLeft: 16 }}>
                      发现 {riskAssessment.alerts.length} 个风险点
                    </Text>
                  )}
                </Col>
                <Col>
                  <Button type="primary" onClick={() => setTradeModalVisible(true)}>
                    <ShoppingCartOutlined /> 交易
                  </Button>
                </Col>
              </Row>
            </Card>
          )}

          {/* 详细内容 */}
          <Tabs defaultActiveKey="positions">
            <TabPane tab="持仓" key="positions">
              <Table
                dataSource={positions}
                columns={positionColumns}
                rowKey="symbol"
                pagination={false}
              />
            </TabPane>

            <TabPane tab="订单" key="orders">
              <Table
                dataSource={orders}
                columns={orderColumns}
                rowKey="order_id"
                pagination={{ pageSize: 10 }}
              />
            </TabPane>

            <TabPane tab="交易历史" key="history">
              <List
                dataSource={tradeHistory}
                renderItem={(item: any) => (
                  <List.Item>
                    <List.Item.Meta
                      title={`${item.symbol} - ${item.side === 'buy' ? '买入' : '卖出'}`}
                      description={item.timestamp}
                    />
                    <div>
                      <Text>{item.shares}股 @ ¥{item.price}</Text>
                      <Text type="secondary" style={{ marginLeft: 16 }}>
                        总额: ¥{item.amount}
                      </Text>
                    </div>
                  </List.Item>
                )}
              />
            </TabPane>

            <TabPane tab="风险分析" key="risk">
              <Row gutter={16}>
                <Col span={12}>
                  <Card title="组合分析" size="small">
                    <p>持仓数量: {portfolioAnalysis.position_count}</p>
                    <p>分散度得分: {portfolioAnalysis.diversification_score}</p>
                    <p>最大持仓: {portfolioAnalysis.largest_position}</p>
                    <p>最佳表现: {portfolioAnalysis.best_performer}</p>
                    <p>最差表现: {portfolioAnalysis.worst_performer}</p>
                  </Card>
                </Col>
                <Col span={12}>
                  <Card title="风险预警" size="small">
                    {riskAssessment.alerts?.map((alert: any, index: number) => (
                      <div key={index} style={{ marginBottom: 8 }}>
                        <Tag color={getRiskLevelColor(alert.level)}>{alert.level}</Tag>
                        <Text>{alert.message}</Text>
                      </div>
                    ))}
                    {(!riskAssessment.alerts || riskAssessment.alerts.length === 0) && (
                      <Text type="secondary">暂无风险预警</Text>
                    )}
                  </Card>
                </Col>
              </Row>
            </TabPane>
          </Tabs>
        </>
      )}

      {/* 交易弹窗 */}
      <Modal
        title="交易"
        open={tradeModalVisible}
        onCancel={() => setTradeModalVisible(false)}
        footer={null}
      >
        <Form form={tradeForm} onFinish={handleTrade} layout="vertical">
          <Form.Item
            name="symbol"
            label="股票代码"
            rules={[{ required: true, message: '请输入股票代码' }]}
          >
            <InputNumber style={{ width: '100%' }} placeholder="如: 600519" />
          </Form.Item>

          <Form.Item
            name="side"
            label="交易方向"
            rules={[{ required: true, message: '请选择方向' }]}
          >
            <Select>
              <Select.Option value="buy">买入</Select.Option>
              <Select.Option value="sell">卖出</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="shares"
            label="股数"
            rules={[{ required: true, message: '请输入股数' }]}
          >
            <InputNumber style={{ width: '100%' }} min={1} step={100} />
          </Form.Item>

          <Form.Item name="order_type" label="订单类型" initialValue="market">
            <Select>
              <Select.Option value="market">市价单</Select.Option>
              <Select.Option value="limit">限价单</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prev, curr) => prev.order_type !== curr.order_type}
          >
            {({ getFieldValue }) =>
              getFieldValue('order_type') === 'limit' ? (
                <Form.Item name="price" label="限价" rules={[{ required: true }]}>
                  <InputNumber style={{ width: '100%' }} precision={2} />
                </Form.Item>
              ) : null
            }
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              提交订单
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}