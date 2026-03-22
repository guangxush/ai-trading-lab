import React, { useState, useEffect } from 'react'
import {
  Card, List, Tag, Button, Modal, Form, Input, Select,
  Rate, message, Typography, Spin, Tabs, Statistic, Row, Col
} from 'antd'
import {
  DownloadOutlined, UploadOutlined, StarOutlined,
  SearchOutlined, AppstoreOutlined
} from '@ant-design/icons'
import axios from 'axios'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input

const API_BASE = import.meta.env.VITE_API_BASE || ''

interface SkillMeta {
  id: string
  name: string
  version: string
  description: string
  author: string
  category: string
  tags: string[]
  downloads: number
  rating: number
  rating_count: number
}

export const Skills: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [skills, setSkills] = useState<SkillMeta[]>([])
  const [categories, setCategories] = useState<any[]>([])
  const [popularTags, setPopularTags] = useState<any[]>([])
  const [stats, setStats] = useState<any>({})
  const [searchText, setSearchText] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>()
  const [uploadModalVisible, setUploadModalVisible] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedSkill, setSelectedSkill] = useState<SkillMeta | null>(null)
  const [uploadForm] = Form.useForm()

  const fetchSkills = async (category?: string, search?: string) => {
    setLoading(true)
    try {
      const params: any = { limit: 50 }
      if (category) params.category = category
      if (search) params.search = search

      const response = await axios.get(`${API_BASE}/api/skill/marketplace/list`, { params })
      const data = response.data

      setSkills(data.skills || [])
      setCategories(data.categories || [])
      setPopularTags(data.popular_tags || [])
    } catch (error) {
      // 如果 marketplace 没有 SKILL，使用内置 SKILL 列表
      try {
        const builtinResponse = await axios.get(`${API_BASE}/api/skill/list`)
        setSkills(builtinResponse.data.skills || [])
      } catch (e) {
        message.error('获取 SKILL 列表失败')
      }
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/skill/marketplace/stats`)
      setStats(response.data)
    } catch (error) {
      // 忽略错误
    }
  }

  useEffect(() => {
    fetchSkills()
    fetchStats()
  }, [])

  const handleSearch = () => {
    fetchSkills(selectedCategory, searchText)
  }

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category === 'all' ? undefined : category)
    fetchSkills(category === 'all' ? undefined : category, searchText)
  }

  const handleUpload = async (values: any) => {
    try {
      await axios.post(`${API_BASE}/api/skill/marketplace/upload`, values)
      message.success('上传成功')
      setUploadModalVisible(false)
      uploadForm.resetFields()
      fetchSkills()
    } catch (error) {
      message.error('上传失败')
    }
  }

  const handleDownload = async (skillId: string) => {
    try {
      const response = await axios.get(`${API_BASE}/api/skill/marketplace/${skillId}/code`)
      const code = response.data.code

      // 下载文件
      const blob = new Blob([code], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${skillId}.py`
      a.click()
      URL.revokeObjectURL(url)

      message.success('下载成功')
    } catch (error) {
      message.error('下载失败')
    }
  }

  const handleRating = async (skillId: string, score: number) => {
    try {
      await axios.post(`${API_BASE}/api/skill/marketplace/${skillId}/rate`, {
        skill_id: skillId,
        score
      })
      message.success('评分成功')
      fetchSkills()
    } catch (error) {
      message.error('评分失败')
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

  const showDetail = (skill: SkillMeta) => {
    setSelectedSkill(skill)
    setDetailModalVisible(true)
  }

  return (
    <div>
      <Title level={2}>
        <AppstoreOutlined /> SKILL 市场
      </Title>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic title="SKILL 总数" value={stats.total_skills || skills.length} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="总下载量" value={stats.total_downloads || 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="分类数量" value={stats.categories || categories.length} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="平均评分" value={stats.avg_rating || 0} suffix="/ 5" />
          </Card>
        </Col>
      </Row>

      {/* 搜索和筛选 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Input
              placeholder="搜索 SKILL..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={e => setSearchText(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
          </Col>
          <Col>
            <Select
              style={{ width: 150 }}
              placeholder="选择分类"
              value={selectedCategory}
              onChange={handleCategoryChange}
              allowClear
            >
              <Select.Option value="all">全部分类</Select.Option>
              {categories.map(cat => (
                <Select.Option key={cat.id} value={cat.id}>
                  {cat.name}
                </Select.Option>
              ))}
            </Select>
          </Col>
          <Col>
            <Button type="primary" onClick={() => setUploadModalVisible(true)}>
              <UploadOutlined /> 上传 SKILL
            </Button>
          </Col>
        </Row>
      </Card>

      {/* SKILL 列表 */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: 50 }}>
          <Spin size="large" />
        </div>
      ) : (
        <List
          grid={{ gutter: 16, xs: 1, sm: 2, md: 2, lg: 3, xl: 4, xxl: 4 }}
          dataSource={skills}
          renderItem={skill => (
            <List.Item>
              <Card
                hoverable
                title={
                  <span>
                    {skill.name}
                    <Tag color={getCategoryColor(skill.category)} style={{ marginLeft: 8 }}>
                      {skill.category}
                    </Tag>
                  </span>
                }
                extra={<Tag>v{skill.version}</Tag>}
                actions={[
                  <Button
                    key="detail"
                    type="link"
                    size="small"
                    onClick={() => showDetail(skill)}
                  >
                    详情
                  </Button>,
                  <Button
                    key="download"
                    type="link"
                    size="small"
                    icon={<DownloadOutlined />}
                    onClick={() => handleDownload(skill.id || skill.name)}
                  >
                    {skill.downloads || 0}
                  </Button>,
                  <Rate
                    key="rating"
                    disabled
                    value={skill.rating || 0}
                    style={{ fontSize: 12 }}
                    allowHalf
                  />,
                ]}
              >
                <Paragraph ellipsis={{ rows: 2 }} style={{ marginBottom: 8, minHeight: 44 }}>
                  {skill.description || '暂无描述'}
                </Paragraph>
                <div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {skill.author}
                  </Text>
                  {skill.tags?.slice(0, 3).map(tag => (
                    <Tag key={tag} style={{ marginLeft: 4, fontSize: 11 }}>
                      {tag}
                    </Tag>
                  ))}
                </div>
              </Card>
            </List.Item>
          )}
        />
      )}

      {!loading && skills.length === 0 && (
        <Card>
          <div style={{ textAlign: 'center', padding: 50, color: '#999' }}>
            <p>暂无 SKILL</p>
            <Button type="primary" onClick={() => setUploadModalVisible(true)}>
              上传第一个 SKILL
            </Button>
          </div>
        </Card>
      )}

      {/* 上传弹窗 */}
      <Modal
        title="上传 SKILL"
        open={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        footer={null}
        width={700}
      >
        <Form form={uploadForm} onFinish={handleUpload} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name"
                label="SKILL 名称"
                rules={[{ required: true, message: '请输入名称' }]}
              >
                <Input placeholder="如：my_strategy" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="version"
                label="版本号"
                rules={[{ required: true, message: '请输入版本号' }]}
                initialValue="1.0.0"
              >
                <Input placeholder="如：1.0.0" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="description" label="描述">
            <TextArea rows={2} placeholder="简要描述 SKILL 功能" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="category" label="分类" initialValue="general">
                <Select>
                  <Select.Option value="analysis">技术分析</Select.Option>
                  <Select.Option value="backtest">策略回测</Select.Option>
                  <Select.Option value="trading">交易策略</Select.Option>
                  <Select.Option value="risk">风险管理</Select.Option>
                  <Select.Option value="general">通用工具</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="author" label="作者">
                <Input placeholder="作者名称" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="code"
            label="Python 代码"
            rules={[{ required: true, message: '请输入代码' }]}
          >
            <TextArea
              rows={10}
              placeholder="请输入 SKILL Python 代码，必须继承 BaseSkill 类"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              提交
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 详情弹窗 */}
      <Modal
        title={selectedSkill?.name}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
      >
        {selectedSkill && (
          <div>
            <Paragraph>
              <Text strong>版本：</Text>{selectedSkill.version}
            </Paragraph>
            <Paragraph>
              <Text strong>作者：</Text>{selectedSkill.author}
            </Paragraph>
            <Paragraph>
              <Text strong>分类：</Text>
              <Tag color={getCategoryColor(selectedSkill.category)}>
                {selectedSkill.category}
              </Tag>
            </Paragraph>
            <Paragraph>
              <Text strong>下载量：</Text>{selectedSkill.downloads || 0}
            </Paragraph>
            <Paragraph>
              <Text strong>评分：</Text>
              <Rate disabled value={selectedSkill.rating || 0} allowHalf />
              <Text type="secondary" style={{ marginLeft: 8 }}>
                ({selectedSkill.rating_count || 0} 人评分)
              </Text>
            </Paragraph>
            <Paragraph>
              <Text strong>描述：</Text>
              <br />
              {selectedSkill.description || '暂无描述'}
            </Paragraph>
            {selectedSkill.tags?.length > 0 && (
              <Paragraph>
                <Text strong>标签：</Text>
                {selectedSkill.tags.map(tag => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </Paragraph>
            )}

            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={() => handleDownload(selectedSkill.id || selectedSkill.name)}
              block
            >
              下载 SKILL
            </Button>
          </div>
        )}
      </Modal>
    </div>
  )
}