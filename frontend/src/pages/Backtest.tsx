import React from 'react'
import { Card, Typography } from 'antd'

const { Title, Paragraph } = Typography

export const Backtest: React.FC = () => {
  return (
    <div>
      <Title level={2}>📈 策略回测</Title>

      <Card>
        <Paragraph>
          策略回测模块正在开发中...
        </Paragraph>
        <Paragraph type="secondary">
          即将支持：
        </Paragraph>
        <ul>
          <li>历史数据回测</li>
          <li>策略参数优化</li>
          <li>收益风险分析</li>
          <li>可视化报告</li>
        </ul>
      </Card>
    </div>
  )
}