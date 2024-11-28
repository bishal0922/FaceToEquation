import EquationGraph from './components/EquationGraph'

export default function Home() {
  return (
    <>
    Hello world
    {equations && (
  <EquationGraph 
    equations={equations} 
    points={equations.outline_points} 
  />
)}
    </>
   
  );
}
