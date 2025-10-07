/**
 * HTTPS长连接性能测试脚本
 * 测试HTTP/2、Keep-Alive等优化效果
 */

// 测试配置
const TEST_CONFIG = {
  baseUrl: 'https://do-not-go-to.icu',
  testCount: 10,
  concurrentRequests: 5
};

// 性能测试函数
async function testHttpsPerformance() {
  console.log('🚀 开始HTTPS长连接性能测试...\n');
  
  // 1. 测试HTTP/2支持
  console.log('📡 测试HTTP/2协议支持...');
  try {
    const response = await fetch(`${TEST_CONFIG.baseUrl}/health`);
    const protocol = response.headers.get('alt-svc') ? 'HTTP/2' : 'HTTP/1.1';
    console.log(`✅ 协议版本: ${protocol}`);
  } catch (error) {
    console.log(`❌ 协议测试失败: ${error.message}`);
  }
  
  // 2. 测试连接复用效果
  console.log('\n🔄 测试连接复用效果...');
  const startTime = Date.now();
  const promises = [];
  
  for (let i = 0; i < TEST_CONFIG.testCount; i++) {
    const promise = fetch(`${TEST_CONFIG.baseUrl}/health`)
      .then(response => ({
        status: response.status,
        time: Date.now() - startTime,
        headers: Object.fromEntries(response.headers.entries())
      }))
      .catch(error => ({
        error: error.message,
        time: Date.now() - startTime
      }));
    promises.push(promise);
    
    // 错开请求，测试连接复用
    if (i % TEST_CONFIG.concurrentRequests === 0) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }
  
  const results = await Promise.all(promises);
  const endTime = Date.now();
  
  // 3. 分析结果
  console.log('\n📊 性能测试结果:');
  console.log(`总耗时: ${endTime - startTime}ms`);
  console.log(`平均响应时间: ${results.reduce((sum, r) => sum + (r.time || 0), 0) / results.length}ms`);
  console.log(`成功请求: ${results.filter(r => r.status === 200).length}/${results.length}`);
  
  // 4. 检查长连接头部
  const successResult = results.find(r => r.status === 200);
  if (successResult && successResult.headers) {
    console.log('\n🔍 响应头部分析:');
    console.log(`Connection: ${successResult.headers.connection || 'N/A'}`);
    console.log(`Keep-Alive: ${successResult.headers['keep-alive'] || 'N/A'}`);
    console.log(`Cache-Control: ${successResult.headers['cache-control'] || 'N/A'}`);
  }
  
  // 5. 测试静态资源缓存
  console.log('\n💾 测试静态资源缓存...');
  try {
    const staticResponse = await fetch(`${TEST_CONFIG.baseUrl}/`);
    console.log(`静态资源状态: ${staticResponse.status}`);
    console.log(`缓存控制: ${staticResponse.headers.get('cache-control') || 'N/A'}`);
  } catch (error) {
    console.log(`❌ 静态资源测试失败: ${error.message}`);
  }
  
  console.log('\n✅ 性能测试完成！');
}

// 在浏览器控制台中运行
if (typeof window !== 'undefined') {
  // 浏览器环境
  window.testHttpsPerformance = testHttpsPerformance;
  console.log('💡 在浏览器控制台中运行: testHttpsPerformance()');
} else {
  // Node.js环境
  testHttpsPerformance().catch(console.error);
}