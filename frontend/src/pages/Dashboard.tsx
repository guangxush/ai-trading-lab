import React, { useState } from 'react'
import { Input, Row, Col, Card, List, Spin, message } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import { searchStock, getQuote } from '../api/market'

const { Search } = Input

interface StockInfo {
  symbol: string
  name: string
  market: string
}

interface QuoteData {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
}

export const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [stocks, setStocks] = useState<StockInfo[]>([])
  const [quotes, setQuotes] = useState<Record<string, QuoteData>>({})

  const handleSearch = async (value: string) => {
    if (!value.trim()) return

    setLoading(true)
    try {
      const results = await searchStock(value)
      setStocks(results.results || [])

      // 批量获取行情
      for (const stock of results.results?.slice(0, 6) || []) {
        const quote = await getQuote(stock.symbol)
        if (quote) {
          setQuotes(prev => ({
            ...prev,
            [stock.symbol]: quote,
          }))
        }
      }
    } catch (error) {
      message.error('搜索失败')
    } finally {
      setLoading(false)
    }
  }

  const formatChange = (change: number, percent: number) => {
    const color = change >= 0 ? '#f5222d' : '#52c41a'
    const sign = change >= 0 ? '+' : ''
    return (
      <span style={{ color }}>
        {sign}{change.toFixed(2)} ({sign}{percent.toFixed(2)}%)
      </span>
    )
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>📊 大盘监控</h2>

      <Search
        placeholder="搜索股票代码或名称，如：600519、茅台"
        allowClear
        enterButton={<><SearchOutlined /> 搜索</>}
        size="large"
        loading={loading}
        onSearch={handleSearch}
        style={{ maxWidth: 600, marginBottom: 24 }}
      />

      {loading ? (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <Spin size="large" />
        </div>
      ) : stocks.length > 0 ? (
        <Row gutter={[16, 16]}>
          {stocks.slice(0, 6).map(stock => {
            const quote = quotes[stock.symbol]
            return (
              <Col key={stock.symbol} xs={24} sm={12} md={8} lg={8}>
                <Card
                  hoverable
                  title={`${stock.name} (${stock.symbol})`}
                  size="small"
                >
                  {quote ? (
                    <div>
                      <div style={{ fontSize: 24, fontWeight: 'bold' }}>
                        ¥{quote.price.toFixed(2)}
                      </div>
                      <div style={{ marginTop: 8 }}>
                        {formatChange(quote.change, quote.change_percent)}
                      </div>
                      <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
                        成交量: {(quote.volume / 10000).toFixed(0)}万
                      </div>
                    </div>
                  ) : (
                    <div style={{ color: '#999' }}>加载中...</div>
                  )}
                </Card>
              </Col>
            )
          })}
        </Row>
      ) : (
        <Card>
          <div style={{ textAlign: 'center', padding: 50, color: '#999' }}>
            <p>📈 搜索股票开始监控</p>
            <p style={{ fontSize: 12 }}>
              支持A股市场，输入股票代码或名称搜索
            </p>
          </div>
        </Card>
      )}

      {stocks.length > 6 && (
        <Card title="更多结果" style={{ marginTop: 16 }}>
          <List
            dataSource={stocks.slice(6)}
            renderItem={item => (
              <List.Item>
                <span>{item.name}</span>
                <span style={{ color: '#999' }}>{item.symbol}</span>
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  )
}