export function optionalNumber(value) {
  return value === '' || value === null || value === undefined ? null : Number(value)
}

export function formatNumber(value, digits = 4) {
  if (value === null || value === undefined) {
    return '未填写'
  }
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  })
}

export function statusMeta(status) {
  return {
    pending: { label: '待审核', className: 'is-pending' },
    approved: { label: '已通过', className: 'is-approved' },
    rejected: { label: '已打回', className: 'is-rejected' }
  }[status] ?? { label: status, className: '' }
}

export function adviceMeta(advice) {
  return {
    buy: { label: '买入', className: 'is-buy' },
    sell: { label: '卖出', className: 'is-sell' },
    hold: { label: '持有', className: 'is-hold' }
  }[advice] ?? { label: advice, className: '' }
}
