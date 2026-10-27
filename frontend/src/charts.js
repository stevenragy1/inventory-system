// Register the Chart.js parts used by the app. Import this file before any chart.
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

// Series colors come from the fixed palette in the plan. Canvas cannot read CSS variables.
export const SERIES_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"];
// Each color also gets a pattern for color-blind readers (see the legend).
export const SERIES_LABELS = ["solid", "striped", "dotted", "hatched"];

export default ChartJS;
