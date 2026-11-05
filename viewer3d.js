import*as THREE from'three';import{OrbitControls}from'./vendor/OrbitControls.js';import{GLTFLoader}from'./vendor/GLTFLoader.js';import{RoomEnvironment}from'./vendor/RoomEnvironment.js';
export function mount(box,o={}){return new Promise((res,rej)=>{
const ren=new THREE.WebGLRenderer({antialias:true,alpha:true});ren.setPixelRatio(Math.min(1.6,devicePixelRatio||1));ren.outputColorSpace=THREE.SRGBColorSpace;ren.toneMapping=THREE.ACESFilmicToneMapping;ren.toneMappingExposure=1.05;
const sc=new THREE.Scene();sc.environment=new THREE.PMREMGenerator(ren).fromScene(new RoomEnvironment,.04).texture;sc.add(new THREE.HemisphereLight(0xffffff,0xc9c2c4,.55));const dl=new THREE.DirectionalLight(0xffffff,1.2);dl.position.set(2,3,2.5);sc.add(dl);
const cam=new THREE.PerspectiveCamera(32,1,.01,100),ctl=new OrbitControls(cam,ren.domElement);Object.assign(ctl,{enableDamping:true,dampingFactor:.08,autoRotate:!!o.auto,autoRotateSpeed:1.4,enablePan:!!o.pan,maxPolarAngle:Math.PI*.52});
ctl.addEventListener('start',()=>{ctl.autoRotate=false});
const fit=()=>{const w=box.clientWidth,h=box.clientHeight;if(!w||!h)return;ren.setSize(w,h);cam.aspect=w/h;cam.updateProjectionMatrix()};
new GLTFLoader().load(o.url||'machine.glb',g=>{const root=g.scene;root.rotation.x=-Math.PI/2;const holder=new THREE.Group();holder.add(root);sc.add(holder);
root.updateMatrixWorld(true);const fb=new THREE.Box3();root.traverse(n=>{if(n.name&&n.name.startsWith('frame__'))fb.expandByObject(n)});const unit=(fb.max.x-fb.min.x)/485||1;let bb=new THREE.Box3().setFromObject(root);const sz=bb.getSize(new THREE.Vector3()),k=1.6/Math.max(sz.x,sz.y,sz.z);holder.scale.setScalar(k);holder.updateMatrixWorld(true);bb=new THREE.Box3().setFromObject(holder);const c=bb.getCenter(new THREE.Vector3());holder.position.sub(c);holder.position.y+=(bb.max.y-bb.min.y)/2*0-0;
root.traverse(e=>{if(e.isMesh){const m=e.material=e.material.clone();m.side=THREE.DoubleSide;if(m.transparent){m.depthWrite=false}}});
cam.position.set(1.5,1.0,1.9);ctl.target.set(0,0,0);if(box.clientWidth<520)cam.position.multiplyScalar(1.25);
box.appendChild(ren.domElement);fit();new ResizeObserver(fit).observe(box);let vis=true;new IntersectionObserver(e=>{vis=e[0].isIntersecting}).observe(box);
(function loop(){requestAnimationFrame(loop);if(!vis||document.hidden)return;ctl.update();ren.render(sc,cam)})();
const orig=new Map();root.traverse(e=>{if(e.isMesh)orig.set(e,{t:e.material.transparent,o:e.material.opacity,d:e.material.depthWrite})});
const nodesOf=key=>{const L=[];root.traverse(n=>{if(n.name&&n.name.startsWith(key+'__'))L.push(n)});return L};
res({root,unit,nodesOf,setOpacity:(key,a)=>{nodesOf(key).forEach(n=>n.traverse(e=>{if(!e.isMesh)return;const o=orig.get(e);if(a>=1){e.material.transparent=o.t;e.material.opacity=o.o;e.material.depthWrite=o.d}else{e.material.transparent=true;e.material.opacity=Math.min(o.o,a);e.material.depthWrite=false}}))},setVisible:(key,on)=>{root.traverse(n=>{if(n.name&&n.name.startsWith(key+'__'))n.visible=on})},ctl,cam});},
p=>{if(o.onProgress&&p.total)o.onProgress(p.loaded/p.total)},rej)})}
