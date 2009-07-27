require 'set'

module BerryMQ
  class MessageQueue
    attr_reader :followers
    def initialize
      @followers = Hash.new {|hash, key| hash[key] = []}
    end

    def size
      @followers.size
    end

    def regist_follower(id_obj, function)
      @followers[id_obj.name].push([id_obj, function])
    end

    def twitter(id_obj, args, kwargs)
      twitter_local(id_obj, args, kwargs)
    end

    def twitter_local(id_obj, args, kwargs)
      message = Message.new(id_obj, args, kwargs)
      wildcard_actions = @followers[nil]
      certain_actions = @followers[id_obj.name]
      remove_list = []
      BerryMQ::Util::iter_chain(wildcard_actions, certain_actions) { |follow|
        following_id, fun = follow
        next unless following_id.is_match(id_obj, message)
        if fun.alive?
          fun.call(message)
        else
          remove_list.push(fun)
        end
      }        
    end
  end

  class Message
    attr_reader :id_obj, :args, :kwargs
    def initialize(id_obj, args, kwargs)
      @id_obj = id_obj
      @args = args
      @kwargs = kwargs
    end
    def name
      @id_obj.name
    end
    def action
      @id_obj.action
    end
    def id
      @id_obj.id_str()
    end
    def twitter(id_obj, args, kwargs)
      MessageQueueRoot.twitter(id_obj, args, kwargs)
    end
    def apply(func)
    end
  end

  module MessageQueueRoot
    @@default_namespace = nil
    @@namespaces = Hash.new {|hash, key| hash[key] = MessageQueue.new}
    def self.twitter(id_obj, args, kwargs)
      namespace = id_obj.namespace
      namespace = @@default_namespace if namespace == nil
      @@namespaces[namespace].twitter(id_obj, args, kwargs)
    end
    def self.[](namespace=nil)
      @@namespaces[namespace]
    end
    def self.regist_follower(target_obj, decorator)
      fun = BerryMQ::WeakRefMethod.new(target_obj, decorator.method_name)
      queue = @@namespaces[decorator.id.namespace]
      queue.regist_follower(decorator.id, fun)
    end
    def self.show_followers
      result = []
      @@namespaces.each { |key, message_queue| 
        queue = ["namespace:%s" % key, []]
        message_queue.followers.each { |name, followers|
          followers.each { |value|
            queue[1].push([value[0].id_str, value[1].method_name])
          }
        }
        result.push(queue)
      }
      result
    end
  end

  module Util
    def self.iter_chain(*sequences, &block)
      sequences.each { |sequence|
        sequence.each(&block) if sequence != nil
      }
    end
  end
end

