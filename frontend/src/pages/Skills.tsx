import React, { useEffect, useState } from 'react'
import { Card, List, Tag, Typography, Spin, message, Button, Modal, Descriptions } from 'antd'
import { PlayCircleOutlined, InfoCircleOutlined } from '@ant-design/icons'
import { listSkills, getSkillDetail } from '../api/skill'

const { Title, Paragraph, Text } = Typography

interface SkillInfo {
  name: string
  version: string
  description: string
  author: string
  category: string
}

export const Skills: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [skills, setSkills] = useState<SkillInfo[]>([])
  const [selectedSkill, setSelectedSkill] = useState<SkillInfo | null>(null)
  const [modalVisible, setModalVisible] = useState(false)

  const fetchSkills = async () => {
    setLoading(true)
    try {
      const result = await listSkills()
      setSkills(result.skills || [])
    } catch (error) {
      message.error('获取SKILL列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSkills()
  }, [])

  const handleViewDetail = async (skillName: string) => {
    try {
      const detail = await getSkillDetail(skillName)
      setSelectedSkill(detail)
      setModalVisible(true)
    } catch (error) {
      message.error('获取详情失败')
    }
  }

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      analysis: 'blue',
      backtest: 'green',
      trading: 'orange',
      risk: 'red',
      general: 'default',
    }
    return colors[category] || 'default'
  }

  return (
    <div>
      <Title level={2}>🧩 SKILL 市场</Title>

      <Paragraph type="secondary">
        浏览和使用已安装的交易策略 SKILL
      </Paragraph>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <Spin size="large" />
        </div>
      ) : (
        <List
          grid={{ gutter: 16, xs: 1, sm: 2, md: 2, lg: 3, xl: 3, xxl: 4 }}
          dataSource={skills}
          renderItem={skill => (
            <List.Item>
              <Card
                hoverable
                actions={[
                  <Button
                    key="detail"
                    type="text"
                    icon={<InfoCircleOutlined />}
                    onClick={() => handleViewDetail(skill.name)}
                  >
                    详情
                  </Button>,
                  <Button
                    key="run"
                    type="text"
                    icon={<PlayCircleOutlined />}
                    onClick={() => message.info('执行功能开发中...')}
                  >
                    执行
                  </Button>,
                ]}
              >
                <Card.Meta
                  title={
                    <span>
                      {skill.name}
                      <Tag
                        color={getCategoryColor(skill.category)}
                        style={{ marginLeft: 8 }}
                      >
                        {skill.category}
                      </Tag>
                    </span>
                  }
                  description={
                    <div>
                      <Paragraph ellipsis={{ rows: 2 }} style={{ marginBottom: 8 }}>
                        {skill.description || '暂无描述'}
                      </Paragraph>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        v{skill.version} · {skill.author}
                      </Text>
                    </div>
                  }
                />
              </Card>
            </List.Item>
          )}
        />
      )}

      {!loading && skills.length === 0 && (
        <Card>
          <div style={{ textAlign: 'center', padding: 50, color: '#999' }}>
            <p>暂无已安装的 SKILL</p>
            <p style={{ fontSize: 12 }}>
              请先在 skills 目录下添加策略
            </p>
          </div>
        </Card>
      )}

      <Modal
        title={selectedSkill?.name}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        {selectedSkill && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="名称">{selectedSkill.name}</Descriptions.Item>
            <Descriptions.Item label="版本">{selectedSkill.version}</Descriptions.Item>
            <Descriptions.Item label="分类">{selectedSkill.category}</Descriptions.Item>
            <Descriptions.Item label="作者">{selectedSkill.author}</Descriptions.Item>
            <Descriptions.Item label="描述">
              {selectedSkill.description || '暂无描述'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}