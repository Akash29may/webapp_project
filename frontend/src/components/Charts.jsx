import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const PALETTE = ['#4f46e5', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export function BarChart({ labels, values, label = 'Count', title }) {
  const data = {
    labels,
    datasets: [
      {
        label,
        data: values,
        backgroundColor: '#4f46e5',
        borderRadius: 4,
      },
    ],
  }
  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: title ? { display: true, text: title } : { display: false },
    },
    scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
  }
  return <Bar data={data} options={options} />
}

export function DoughnutChart({ labels, values, title }) {
  const data = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: PALETTE,
        borderWidth: 1,
      },
    ],
  }
  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'bottom' },
      title: title ? { display: true, text: title } : { display: false },
    },
  }
  return <Doughnut data={data} options={options} />
}
